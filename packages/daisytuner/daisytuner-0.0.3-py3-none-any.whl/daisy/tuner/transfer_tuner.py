import copy
import json
import dace
import math
import torch
import sympy
import requests
import numpy as np

from typing import Dict, List
from scipy.optimize import linear_sum_assignment

from dace.sdfg import infer_types
from dace.transformation import PatternTransformation
from dace.transformation.optimizer import Optimizer
from dace.transformation.auto.auto_optimize import (
    make_transients_persistent,
)
from dace.transformation.dataflow import (
    MapExpansion,
    MapCollapse,
    TrivialMapRangeElimination,
    TrivialMapElimination,
    InLocalStorage,
    OutLocalStorage,
    AccumulateTransient,
)


from dace.sdfg.state import StateSubgraphView
from dace.sdfg.analysis.cutout import SDFGCutout
from dace.frontend.operations import detect_reduction_type
from dace.transformation.optimizer import Optimizer

from daisy import MapNest
from daisy.measure import random_arguments, measure
from daisy.models import Encoding, DaisyNet
from daisy.transformations import MapSchedule


TT_API_URI = "https://daisytuner.com/api/tune"


class TransferTuner:
    def __init__(
        self, hostname: str = None, arch: str = None, verify: bool = False
    ) -> None:
        self._hostname = hostname
        self._arch = arch
        self._verify = verify

        self._model = DaisyNet.create(hostname=self._hostname, arch=self._arch)

    def tune(
        self,
        map_nest: MapNest,
        arguments: Dict = None,
        topK: int = 3,
    ) -> str:
        if arguments is None:
            arguments = random_arguments(map_nest.cutout)

        # Benchmark
        initial_sdfg = map_nest.cutout
        initial_runtime, initial_process_time, _ = measure(
            initial_sdfg,
            arguments=arguments,
        )
        if initial_runtime == math.inf:
            raise ValueError

        nns = self._query_nearest_neighbors(map_nest, topK=topK)
        if not nns:
            return None

        best_schedule = None
        best_runtime = initial_runtime
        best_process_time = initial_process_time
        for nn in nns:
            schedule = json.loads(nn["metadata"]["tuning"]["schedule"])
            try:
                recom = self.apply_schedule(map_nest, schedule, in_place=False)
            except:
                continue

            runtime, process_time, _ = measure(
                recom,
                arguments=arguments,
                timeout=best_process_time * 1.5,
            )
            if runtime == math.inf:
                continue

            if runtime < best_runtime:
                best_runtime = runtime
                best_process_time = process_time
                best_schedule = schedule

        if best_schedule is not None:
            _ = self.apply_schedule(map_nest, best_schedule, in_place=True)

        return best_schedule

    def _query_nearest_neighbors(self, map_nest: MapNest, topK: int) -> Dict:
        emb, _, static_emb, _, arch_emb = self._model.embedding(map_nest)

        if self._hostname is None:
            emb = static_emb
            runner = "__static"
        else:
            runner = arch_emb.tolist()

        payload = {
            "type": "cpu",
            "runner": runner,
            "embedding": emb.tolist(),
            "outermost_dims": len(map_nest.outermost_map.map.params),
            "topK": topK,
            "collections": ["linalg"],
        }
        res = requests.post(TT_API_URI, json=payload)
        if res.status_code != requests.codes.ok:
            raise ValueError("TT request failed")

        return res.json()

    @torch.inference_mode()
    def apply_schedule(
        self, map_nest: MapNest, schedule: List[Dict], in_place: bool = False
    ) -> dace.SDFG:
        if in_place:
            sdfg = map_nest.sdfg
            subgraph_view = map_nest.view
        else:
            schedule = copy.deepcopy(schedule)
            sdfg = copy.deepcopy(map_nest.cutout)
            subgraph_view = StateSubgraphView(
                sdfg.start_state, sdfg.start_state.nodes()
            )

        subgraph_view = TransferTuner._preprocess(sdfg, subgraph_view)

        in_local_buffers = set()
        out_local_buffers = set()
        in_strides, out_strides = TransferTuner._analyze_accesses(map_nest)
        for trans in schedule:
            # Create a temporary SDFG to compute node embeddings on subgraph-only
            cutout_ = SDFGCutout.singlestate_cutout(
                subgraph_view.graph,
                *subgraph_view.nodes(),
                make_copy=False,
                make_side_effects_global=False,
                use_alibi_nodes=False
            )
            map_nest_ = MapNest.create(
                cutout_, cutout_.start_state, build_folder=map_nest.cutout.build_folder
            )

            # Compute node embeddings
            encoding = Encoding(
                map_nest=map_nest_, hostname=self._hostname, arch=self._arch
            )
            encoding.encode()
            data = encoding.torch().to(self._model.device)
            _, _, node_embeddings, *_ = self._model.forward(data)
            node_embeddings = node_embeddings.cpu().numpy().squeeze()

            # Subgraph matching of pattern nodes to actual nodes
            matching = self._subgraph_matching(
                cutout_,
                trans["_subgraph"],
                encoding,
                node_embeddings,
            )
            if matching is None:
                continue

            # Convert node ids back to original SDFG
            trans["_subgraph"] = {}
            for pattern_node, node_id in matching.items():
                node = cutout_.start_state.node(node_id)
                trans["_subgraph"][pattern_node] = subgraph_view.node_id(node)

            # Replace sdfg-specific options
            if not self._find_options(
                sdfg,
                subgraph_view,
                trans,
                in_local_buffers,
                out_local_buffers,
                in_strides,
                out_strides,
            ):
                continue

            # Parse transformation
            try:
                xform = PatternTransformation.from_json(trans)
            except StopIteration:
                # No dace transformation
                if trans["type"] == "MapSchedule":
                    xform = MapSchedule.from_json(trans)
                else:
                    raise ValueError("Unknown transformation")
            xform._sdfg = sdfg
            xform.state_id = sdfg.node_id(subgraph_view.graph)

            if xform.can_be_applied(subgraph_view.graph, sdfg=sdfg, expr_index=0):
                xform.apply(subgraph_view.graph, sdfg)

                # Update state of matching
                if isinstance(xform, InLocalStorage):
                    in_local_buffers.add(xform.array)
                elif isinstance(xform, OutLocalStorage):
                    out_local_buffers.add(xform.array)
                elif isinstance(xform, AccumulateTransient):
                    out_local_buffers.add(xform.array)

                subgraph_view = update_subgraph_view(sdfg, subgraph_view)
            else:
                pass

        TransferTuner._postprocess(sdfg)
        return sdfg

    def _subgraph_matching(
        self,
        sdfg: dace.SDFG,
        pattern_subgraph: Dict,
        encoding: Encoding,
        node_embeddings: np.ndarray,
    ) -> Dict:
        pattern_nodes = list(pattern_subgraph.keys())
        elements = list(
            filter(lambda e: isinstance(e, dace.nodes.Node), encoding.elements())
        )

        cost_matrix = np.zeros((len(pattern_nodes), len(elements)))
        for i in range(cost_matrix.shape[0]):
            pattern_node = pattern_subgraph[pattern_nodes[i]]

            for j in range(cost_matrix.shape[1]):
                element = elements[j]
                element_desc = TransferTuner._element_description(
                    sdfg.start_state, element
                )
                element_embedding = node_embeddings[encoding.index(element)]
                if element_desc["type"] == pattern_node["type"]:
                    if element_desc["scope_levels"] == pattern_node["scope_levels"]:
                        cost_matrix[i, j] = np.linalg.norm(
                            (
                                np.array(pattern_node["node_embedding"])
                                - element_embedding
                            ),
                            ord=2.0,
                        )
                        continue

                cost_matrix[i, j] = np.inf

        # Bi-partite matching between pattern node embeddings and node embeddings
        try:
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
        except:
            return None

        subgraph = {}
        for i in range(len(row_ind)):
            pattern_node = pattern_nodes[row_ind[i]]
            element = elements[col_ind[i]]
            element_id = sdfg.start_state.node_id(element)
            subgraph[pattern_node] = element_id

        if len(subgraph) != len(pattern_nodes):
            return None

        return subgraph

    def _find_options(
        self,
        sdfg: dace.SDFG,
        subgraph_view: StateSubgraphView,
        trans: Dict,
        in_local_buffers: set,
        out_local_buffers: set,
        in_strides: Dict,
        out_strides: Dict,
    ) -> None:
        subgraph = trans["_subgraph"]
        transformation = trans["transformation"]

        if transformation == "MapDimShuffle":
            map_entry = subgraph_view.graph.node(subgraph["0"])
            map_params = [map_entry.map.params[i] for i in trans["parameters"]]
            trans["parameters"] = map_params
        elif transformation == "MapSchedule":
            trans["unroll"] = False
        elif transformation == "StripMining":
            map_entry = subgraph_view.graph.node(subgraph["0"])
            dim_idx = trans["dim_idx"]
            tile_size = int(trans["tile_size"])
            start, stop, step = map_entry.map.range[dim_idx]
            map_extend = dace.symbolic.int_floor((stop + 1 - start), step)
            map_extend = dace.symbolic.evaluate(map_extend, symbols=sdfg.constants)
            divides_evenly = map_extend / tile_size
            trans["divides_evenly"] = divides_evenly.is_integer
        elif transformation == "MapTiling":
            map_entry = subgraph_view.graph.node(subgraph["0"])
            tile_sizes = trans["tile_sizes"]
            divides_evenly = True
            for i, (start, stop, step) in enumerate(map_entry.map.range):
                map_extend = dace.symbolic.int_floor((stop + 1 - start), step)
                map_extend = dace.symbolic.evaluate(map_extend, symbols=sdfg.constants)
                divisor = map_extend / int(tile_sizes[i])
                divides_evenly = divides_evenly and divisor.is_integer
            trans["divides_evenly"] = divides_evenly
            trans["prefix"] = "tile"
            trans["tile_trivial"] = True
        elif transformation == "Vectorization":
            map_entry = subgraph_view.graph.node(subgraph["0"])
            start, stop, step = map_entry.map.range[-1]
            map_extend = dace.symbolic.int_floor((stop + 1 - start), step)
            map_extend = dace.symbolic.evaluate(map_extend, symbols=sdfg.constants)
            divisor = map_extend / int(trans["vector_len"])
            divides_evenly = divisor.is_integer
            trans["preamble"] = False
            trans["postamble"] = not divides_evenly

            tasklet: dace.nodes.Tasklet = next(
                subgraph_view.graph.out_edges(map_entry).__iter__()
            ).dst
            code = tasklet.code.as_string
            if "min" in code or "max" in code:
                return False

            wcr_edge = next(subgraph_view.graph.out_edges(tasklet).__iter__())
            memlet: dace.Memlet = wcr_edge.data
            if memlet.wcr is not None and ("min" in memlet.wcr or "max" in memlet.wcr):
                return False
        elif transformation == "InLocalStorage":
            first_map_entry = subgraph_view.graph.node(subgraph["0"])
            second_map_entry = subgraph_view.graph.node(subgraph["1"])

            # Potential arrays
            options = set(
                [
                    edge.data.data
                    for edge in subgraph_view.graph.edges_between(
                        first_map_entry, second_map_entry
                    )
                    if edge.data is not None
                    and edge.data.data is not None
                    and edge.data.wcr is None
                ]
            )

            # Arrays sorted by stride of innermost map
            strides = sorted(in_strides.items(), key=lambda item: item[1], reverse=True)

            # Pick from options according to strides
            array = None
            for option, _ in strides:
                if option not in options or option in in_local_buffers:
                    continue

                array = option
                break

            if array is None:
                # Try again with a second buffer
                for option, _ in strides:
                    if option not in options:
                        continue

                    array = option
                    break

                if array is None:
                    return False

            trans["array"] = array
        elif transformation == "OutLocalStorage":
            first_map_exit = subgraph_view.graph.node(subgraph["0"])
            second_map_exit = subgraph_view.graph.node(subgraph["1"])

            # Potential arrays
            options = set(
                [
                    edge.data.data
                    for edge in subgraph_view.graph.edges_between(
                        first_map_exit, second_map_exit
                    )
                    if edge.data is not None
                    and edge.data.data is not None
                    and edge.data.wcr is None
                ]
            )

            # Arrays sorted by stride of innermost map
            strides = sorted(
                out_strides.items(), key=lambda item: item[1], reverse=True
            )

            # Pick from options according to strides
            array = None
            for option, _ in strides:
                if option not in options or option in out_local_buffers:
                    continue

                array = option
                break

            if array is None:
                # Try again with a second buffer
                for option, _ in strides:
                    if option not in options:
                        continue

                    array = option
                    break

                if array is None:
                    return False

            trans["array"] = array
        elif transformation == "AccumulateTransient":
            first_map_exit = subgraph_view.graph.node(subgraph["0"])
            second_map_exit = subgraph_view.graph.node(subgraph["1"])

            # Heuristic: largest strided access
            edges = [
                (e, e.data.get_stride(sdfg, first_map_exit.map, dim=-1))
                for e in subgraph_view.graph.edges_between(
                    first_map_exit, second_map_exit
                )
                if e.data.data is not None and e.data.wcr is not None
            ]
            edges = sorted(
                edges,
                key=lambda item: int(
                    dace.symbolic.evaluate(item[1], symbols=sdfg.constants)
                ),
                reverse=True,
            )
            if not edges or edges[0][1] >= 1:
                return False

            trans["array"] = edges[0][0].data.data

            edge = edges[0][0]
            reduction_type = detect_reduction_type(edge.data.wcr)
            if reduction_type == dace.dtypes.ReductionType.Custom:
                trans["identity"] = None
            else:
                dtype = sdfg.arrays[trans["array"]].dtype
                identity = dace.dtypes.reduction_identity(dtype, reduction_type)
                trans["identity"] = identity

        return True

    @staticmethod
    def _analyze_accesses(map_nest: MapNest) -> Dict:
        in_arrays = {}
        out_arrays = {}
        for dnode in map_nest.view.data_nodes():
            if map_nest.view.entry_node(dnode) is not None:
                continue

            if map_nest.view.in_degree(dnode) == 0:
                in_arrays[dnode.data] = 0
            elif map_nest.view.out_degree(dnode) == 0:
                out_arrays[dnode.data] = 0

        for innermost_map in map_nest.innermost_maps:
            for edge in map_nest.view.out_edges(innermost_map):
                if edge.data.data is None:
                    continue

                stride = edge.data.get_stride(map_nest.sdfg, innermost_map.map, dim=-1)
                # Overapproximate
                stride = stride.replace(sympy.Max, sympy.Add)
                stride = stride.replace(sympy.Min, sympy.Add)

                stride = int(
                    dace.symbolic.evaluate(stride, symbols=map_nest.sdfg.constants)
                )
                if stride == 0:
                    stride = math.inf

                if in_arrays[edge.data.data] < stride:
                    in_arrays[edge.data.data] = stride

        for innermost_map in map_nest.innermost_maps:
            for edge in map_nest.view.in_edges(map_nest.view.exit_node(innermost_map)):
                if edge.data.data is None:
                    continue

                stride = edge.data.get_stride(map_nest.sdfg, innermost_map.map, dim=-1)
                stride = int(
                    dace.symbolic.evaluate(stride, symbols=map_nest.sdfg.constants)
                )
                if stride == 0:
                    stride = math.inf

                if out_arrays[edge.data.data] < stride:
                    out_arrays[edge.data.data] = stride

        return in_arrays, out_arrays

    @staticmethod
    def _element_description(state: dace.SDFGState, element: dace.nodes.Node) -> Dict:
        desc = element.to_json(state)

        scope_levels = 0
        if "scope_entry" in desc:
            scope_entry = desc["scope_entry"]
            while not scope_entry is None:
                scope_levels += 1

                scope = state.node(int(scope_entry))
                scope_entry = scope.to_json(state)["scope_entry"]

        cs = {"type": desc["type"], "scope_levels": scope_levels}
        return cs

    @classmethod
    def _preprocess(
        cls, sdfg: dace.SDFG, subgraph_view: StateSubgraphView
    ) -> StateSubgraphView:
        for node in subgraph_view.nodes():
            if not isinstance(node, dace.nodes.MapEntry):
                continue

            node.schedule = dace.ScheduleType.Sequential
            node.collapse = 1

        subgraph_view = apply_transformations_repeated_on_subgraph(
            TrivialMapElimination, sdfg, subgraph_view
        )
        subgraph_view = apply_transformations_repeated_on_subgraph(
            MapExpansion, sdfg, subgraph_view
        )

        return subgraph_view

    @classmethod
    def _postprocess(cls, sdfg: dace.SDFG):
        sdfg.apply_transformations_repeated(
            (TrivialMapRangeElimination, TrivialMapElimination)
        )

        infer_types.infer_connector_types(sdfg)
        infer_types.set_default_schedule_and_storage_types(sdfg, None)

        for nsdfg in sdfg.all_sdfgs_recursive():
            nsdfg.openmp_sections = False

        make_transients_persistent(sdfg, dace.DeviceType.CPU)
        collapse_adjacent_openmp_maps(sdfg)

        sdfg.simplify()


def collapse_adjacent_openmp_maps(sdfg: dace.SDFG):
    while True:
        xforms_ = list(Optimizer(sdfg).get_pattern_matches(patterns=[MapCollapse]))
        xforms = []
        for xform in xforms_:
            om = xform.outer_map_entry
            im = xform.inner_map_entry

            if (
                im.map.schedule != dace.ScheduleType.CPU_Multicore
                or om.map.schedule != dace.ScheduleType.CPU_Multicore
            ):
                continue

            if im.map.collapse != len(im.map.params) or om.map.collapse != len(
                om.map.params
            ):
                continue

            xforms.append(xform)
            break

        if len(xforms) == 0:
            break

        xform = xforms[0]
        collapsed_me, _ = xform.apply(xform._sdfg.node(xform.state_id), xform._sdfg)
        collapsed_me.map.collapse = len(collapsed_me.map.params)


def apply_transformations_repeated_on_subgraph(
    transformation: PatternTransformation,
    sdfg: dace.SDFG,
    subgraph_view: StateSubgraphView,
) -> StateSubgraphView:
    while True:
        xforms = Optimizer(sdfg).get_pattern_matches(patterns=(transformation,))
        applied = False
        for xform in xforms:
            # check same state
            if xform._sdfg != sdfg or sdfg.node(xform.state_id) != subgraph_view.graph:
                continue

            contained = True
            for _, node_id in xform.subgraph.items():
                if subgraph_view.graph.node(node_id) not in subgraph_view.nodes():
                    contained = False
                    break

            if not contained:
                continue

            xform.apply(subgraph_view.graph, sdfg)
            applied = True
            break

        if not applied:
            break

    return update_subgraph_view(sdfg, subgraph_view)


def update_subgraph_view(
    sdfg: dace.SDFG, subgraph_view: StateSubgraphView
) -> StateSubgraphView:
    # TODO: Find better solution

    state: dace.SDFGState = subgraph_view.graph
    map_entry = None
    for node in subgraph_view.nodes():
        if node not in state.nodes():
            continue

        if isinstance(node, (dace.nodes.MapExit, dace.nodes.AccessNode)):
            continue

        map_entry = node
        break

    # Assumption, working on top-level maps only
    while state.entry_node(map_entry) is not None:
        map_entry = state.entry_node(map_entry)

    map_exit = state.exit_node(map_entry)
    subgraph_nodes = set(state.all_nodes_between(map_entry, map_exit))
    subgraph_nodes.add(map_entry)
    subgraph_nodes.add(map_exit)

    for edge in state.in_edges(map_entry):
        subgraph_nodes.add(edge.src)
    for edge in state.out_edges(map_exit):
        subgraph_nodes.add(edge.dst)

    subgraph_nodes = list(subgraph_nodes)

    view: StateSubgraphView = StateSubgraphView(state, subgraph_nodes)
    return view
