from __future__ import annotations

import dace
import copy

from typing import List
from pathlib import Path
from collections import defaultdict

from dace.sdfg.analysis.cutout import SDFGCutout
from dace.sdfg.state import StateSubgraphView


class MapNest(object):

    __create_key = object()

    def __init__(
        self,
        create_key: object,
        sdfg: dace.SDFG,
        state: dace.SDFGState,
        view: StateSubgraphView,
        cutout: dace.SDFG,
    ) -> None:
        assert (
            create_key == MapNest.__create_key
        ), "MapNest objects must be created using MapNest.create"

        self._sdfg = sdfg
        self._state = state
        self._view = view
        self._cutout = cutout

        self._is_chain = True
        maps = set()
        for node in self._view.nodes():
            if not isinstance(node, dace.nodes.MapEntry):
                continue

            if MapNest._is_valid(self._cutout, node):
                maps.add(node)
        assert len(maps) > 0

        # Filter maps that can be encoded
        self._maps = []
        self._maps_tree = defaultdict(list)
        for node in maps:
            parent_map = self._state.entry_node(node)
            if parent_map in maps:
                self._maps_tree[parent_map].append(node)
                self._maps.append(node)
            elif parent_map is None:
                self._maps_tree[None].append(node)
                self._maps.append(node)

        self._outermost_map = self._maps_tree[None][0]
        self._innermost_maps = []
        for map_entry in self._maps:
            if not map_entry in self._maps_tree:
                self._innermost_maps.append(map_entry)

        self._cache_folder = Path(cutout.build_folder) / "daisy"
        self._cache_folder.mkdir(exist_ok=True, parents=False)

    @property
    def view(self) -> StateSubgraphView:
        return self._view

    @property
    def cutout(self) -> dace.SDFG:
        return self._cutout

    @property
    def sdfg(self) -> dace.SDFG:
        return self._sdfg

    @property
    def state(self) -> dace.SDFGState:
        return self._state

    @property
    def hash(self) -> str:
        return self._cutout.hash_sdfg()

    @property
    def name(self) -> str:
        return self._cutout.name

    @property
    def cache_folder(self) -> Path:
        return self._cache_folder

    @property
    def is_chain(self) -> bool:
        return self._is_chain

    @property
    def maps(self) -> List[dace.nodes.MapEntry]:
        return self._maps

    @property
    def maps_tree(self) -> defaultdict(list):
        return self._maps_tree

    @property
    def outermost_map(self) -> dace.nodes.MapEntry:
        return self._outermost_map

    @property
    def innermost_maps(self) -> List[dace.nodes.MapEntry]:
        return self._innermost_maps

    @property
    def levels(self) -> int:
        levels = 1
        current_map = self._innermost_maps[0]
        while self._state.entry_node(current_map) is not None:
            current_map = self._state.entry_node(current_map)
            levels += 1

        return levels

    @classmethod
    def create(
        cls,
        sdfg: dace.SDFG,
        state: dace.SDFGState,
        map_entry: dace.nodes.MapEntry = None,
        build_folder: str = None,
    ) -> MapNest:
        if map_entry is None:
            for node in state.nodes():
                if (
                    not isinstance(node, dace.nodes.MapEntry)
                    or state.entry_node(node) is not None
                ):
                    continue

                if map_entry is not None:
                    raise ValueError("Found multiple candidate map nests in state")

                map_entry = node

        if not (
            isinstance(map_entry, dace.nodes.MapEntry)
            and state.entry_node(map_entry) is None
        ):
            raise ValueError("Not a top-level map entry")

        # Collect all nodes
        map_exit = state.exit_node(map_entry)
        subgraph_nodes = set(state.all_nodes_between(map_entry, map_exit))
        subgraph_nodes.add(map_entry)
        subgraph_nodes.add(map_exit)

        for edge in state.in_edges(map_entry):
            subgraph_nodes.add(edge.src)
        for edge in state.out_edges(map_exit):
            subgraph_nodes.add(edge.dst)

        subgraph_nodes = list(subgraph_nodes)

        # Construct subgraph view and cutout
        view: StateSubgraphView = StateSubgraphView(state, subgraph_nodes)
        cutout: dace.SDFG = SDFGCutout.singlestate_cutout(
            state,
            *subgraph_nodes,
            make_copy=False,
            make_side_effects_global=False,
            use_alibi_nodes=False,
        )
        cutout.name = "maps_" + str(cutout.hash_sdfg()).replace("-", "_")
        cutout.validate()

        if build_folder is None:
            build_folder = Path(sdfg.build_folder) / "daisy" / "maps" / cutout.name

        Path(build_folder).mkdir(exist_ok=True, parents=True)
        cutout.build_folder = str(build_folder)

        loop_nest = MapNest(
            create_key=cls.__create_key,
            sdfg=sdfg,
            state=state,
            view=view,
            cutout=cutout,
        )
        return loop_nest

    @staticmethod
    def _is_valid(cutout: dace.SDFG, map_entry: dace.nodes.MapEntry):
        for start, stop, step in map_entry.map.range:
            if isinstance(start, dace.symbolic.SymExpr):
                start = start.approx
            if isinstance(stop, dace.symbolic.SymExpr):
                stop = stop.approx
            if isinstance(step, dace.symbolic.SymExpr):
                step = step.approx

            map_extend = stop + 1 - start
            try:
                _ = int(dace.symbolic.evaluate(map_extend, symbols=cutout.constants))
            except:
                return False

        return True
