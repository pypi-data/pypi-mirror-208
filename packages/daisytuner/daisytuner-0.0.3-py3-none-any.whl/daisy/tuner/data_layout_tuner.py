import dace
import copy
import torch
import math
import numpy as np
import itertools

from tqdm import tqdm
from typing import Dict, List
from collections import defaultdict

from sklearn.cluster import KMeans

from daisy.map_nest import MapNest
from daisy.analysis import Profiling
from daisy.models import DaisyNet, Encoding
from daisy.measure import (
    create_data_report,
    arguments_from_data_report,
    random_arguments,
    measure,
)


class DataLayoutTuner:
    def __init__(
        self, sdfg: dace.SDFG, hostname: str, arch: str, arguments: Dict = None
    ) -> None:
        if hostname is not None and arch is None:
            raise ValueError("Specify architecture when using hostname")

        self._hostname = hostname
        self._arch = arch

        self._sdfg = sdfg
        self._arguments = arguments
        self._model = DaisyNet.create(arch=self._arch)

        self._groups = {}
        self._map_nests = []
        self._arrays = set()
        self._array_embeddings = {}
        for state in self._sdfg.states():
            for dnode in state.data_nodes():
                if state.entry_node(dnode) is not None:
                    continue

                desc = self._sdfg.arrays[dnode.data]
                if len(desc.shape) < 2:
                    continue

                self._arrays.add(dnode.data)

    def preprocess(self) -> None:
        self._map_nests = []
        for state in self._sdfg.states():
            for node in state.nodes():
                if (
                    not isinstance(node, dace.nodes.MapEntry)
                    or state.entry_node(node) is not None
                ):
                    continue

                map_nest = MapNest.create(self._sdfg, state, map_entry=node)
                self._map_nests.append(map_nest)

        print(
            "Daisy now instruments parts of the SDFG and computes the node embeddings"
        )

        if self._arguments is None:
            self._arguments = random_arguments(self._sdfg)

        with tqdm(total=len(self._map_nests) + 1) as pbar:
            pbar.set_description("Generating data report")

            data_report = self._sdfg.get_instrumented_data()
            if data_report is None:
                data_report = create_data_report(
                    self._sdfg, self._arguments, transients=True
                )
            pbar.update(1)

            pbar.set_description("Profiling map nests")
            self._array_embeddings = {}
            for map_nest in self._map_nests:
                arguments = arguments_from_data_report(map_nest.cutout, data_report)
                arguments = {**self._arguments, **arguments}

                analysis = Profiling(
                    map_nest,
                    arch=self._arch,
                    arguments=arguments,
                )
                try:
                    _ = analysis.analyze()
                except:
                    continue

                encoding = Encoding(
                    map_nest=map_nest, hostname=self._hostname, arch=self._arch
                )
                encoding.encode(cache_only=True)
                with torch.inference_mode():
                    _, embedding, node_embeddings = self._model(encoding.torch())
                    embedding = embedding.cpu().numpy().squeeze()
                    node_embeddings = node_embeddings.cpu().numpy().squeeze()

                    for dnode in map_nest.view.data_nodes():
                        if dnode.data in self._arrays:
                            if dnode.data not in self._array_embeddings:
                                self._array_embeddings[dnode.data] = node_embeddings[
                                    encoding.index(dnode)
                                ]

                pbar.update(1)

            for array in self._arrays:
                if array not in self._array_embeddings:
                    self._array_embeddings[array] = np.random.random((128,))

    def tune(self, k: int = 3) -> None:
        # Pre-partition arrays based on dimensions
        bins = defaultdict(list)
        for array in self._arrays:
            desc = self._sdfg.arrays[array]
            bins[len(desc.shape)].append((array, self._array_embeddings[array]))

        # Partition using k-Means
        self._partitions = {}
        for b in bins:
            arrays, embeddings = zip(*bins[b])
            embeddings = np.array(embeddings)

            kmeans = KMeans(n_clusters=min(k, len(arrays)), random_state=0).fit(
                embeddings
            )

            bin_partitions = defaultdict(list)
            for i, label in enumerate(kmeans.labels_):
                bin_partitions[label].append(arrays[i])

            self._partitions[b] = bin_partitions

        print(self._partitions)

        base_runtime, base_process_time, _ = measure(
            self._sdfg, arguments=self._arguments, measurements=10
        )
        print(base_runtime)

        best_config = None
        best_config_readable = None
        best_runtime = base_runtime
        best_process_time = base_process_time
        for config in tqdm(list(combinations(self._partitions))):
            sdfg = copy.deepcopy(self._sdfg)

            config_readable = []
            for array in config:
                desc = sdfg.arrays[array]
                desc.set_strides_from_layout(*config[array])
                config_readable.append((array, desc.shape, desc.strides))

            runtime, process_time, _ = measure(
                sdfg,
                arguments=self._arguments,
                measurements=10,
                timeout=best_process_time * 1.5,
            )
            print(runtime, config_readable)

            if runtime != math.inf and (best_runtime / runtime) > 1.10:
                best_config = config
                best_config_readable = config_readable
                best_runtime = runtime
                best_process_time = process_time

        print("Best config: ", config)
        if best_config is not None:
            for array in config:
                desc = self._sdfg.arrays[array]
                desc.set_strides_from_layout(*config[array])

        return best_config, best_config_readable


def combinations(partitions: Dict):
    groups = []
    combinations = []
    for dims in partitions:
        for partition in partitions[dims]:
            arrays = partitions[dims][partition]
            groups.append(arrays)

            perms = list(itertools.permutations(list(range(dims))))
            combinations.append(perms)

    for config in itertools.product(*combinations, repeat=1):
        tmp = {}
        for i in range(len(config)):
            arrays = groups[i]
            perm = config[i]
            for array in arrays:
                tmp[array] = perm

        yield tmp
