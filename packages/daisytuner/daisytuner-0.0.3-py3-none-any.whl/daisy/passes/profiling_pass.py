import dace
import pandas as pd

from typing import Any, Dict
from tqdm import tqdm

from dace.transformation import pass_pipeline as ppl

from daisy.map_nest import MapNest
from daisy.utils import host
from daisy.analysis.profiling import Profiling
from daisy.analysis.benchmarking import Benchmarking
from daisy.measure.arguments import (
    random_arguments,
    arguments_from_data_report,
    create_data_report,
)


@dace.properties.make_properties
class ProfilingPass(ppl.Pass):
    """
    Profiles each map nests. If a data report was generated before, input data is taken from the latest report.
    """

    CATEGORY: str = "Performance Modeling"

    recursive = True

    def modifies(self) -> ppl.Modifies:
        return ppl.Modifies.Nothing

    def should_reapply(self, modified: ppl.Modifies) -> bool:
        return ppl.Modifies.Scopes

    def apply_pass(self, sdfg: dace.SDFG, pipeline_results: Dict[str, Any]) -> int:
        map_nests = []
        for nsdfg in sdfg.all_sdfgs_recursive():
            # Check if SDFG is nested in a map scope
            parent_sdfg = nsdfg.parent_sdfg
            if parent_sdfg is not None:
                nsdfg_node = nsdfg.parent_nsdfg_node
                for state in parent_sdfg.states():
                    parent_state = None
                    if nsdfg_node in state.nodes():
                        if nsdfg_node in state:
                            parent_state = state
                            break

                assert parent_state is not None
                scope = parent_state.entry_node(nsdfg_node)
                if isinstance(scope, dace.nodes.MapEntry):
                    # Skip
                    continue

            for state in nsdfg.states():
                for node in state.nodes():
                    if (
                        not isinstance(node, dace.nodes.MapEntry)
                        or state.entry_node(node) is not None
                    ):
                        continue

                    # No init maps
                    if state.in_degree(node) == 0:
                        continue

                    map_nest = MapNest.create(nsdfg, state, map_entry=node)
                    map_nests.append(map_nest)

            print("Profiling map nests. This may take a while...")
            with tqdm(total=len(map_nests) + 1) as pbar:
                pbar.set_description("Generating data report")

                input_arguments = None
                data_report = sdfg.get_instrumented_data()
                if data_report is None:
                    input_arguments = random_arguments(sdfg)
                    data_report = create_data_report(
                        sdfg, input_arguments, transients=True
                    )

                pbar.update(1)

                pbar.set_description("Profiling map nests")
                profiles = None
                for map_nest in map_nests:
                    arguments = arguments_from_data_report(map_nest.cutout, data_report)
                    if input_arguments is not None:
                        arguments = {**arguments, **input_arguments}

                    analysis = Profiling(
                        map_nest,
                        arguments=arguments,
                    )
                    _ = analysis.analyze()
                    metrics = analysis.performance_metrics()

                    if profiles is None:
                        profiles = pd.DataFrame(columns=metrics.columns)

                    profiles.loc[map_nest.hash] = metrics.iloc[0]
                    pbar.update(1)

        # Performance modeling
        print("Roofline modeling...")
        benchmarks = Benchmarking(hostname=host()).analyze()
        max_bandwidth = benchmarks["stream_triad"]
        max_flops = benchmarks["peakflops_avx"]

        profiles.loc[:, "peak performance"] = (
            max_bandwidth * profiles.loc[:, "operational_intensity"]
        )
        profiles.loc[:, "peak performance"] = profiles.loc[:, "peak performance"].clip(
            upper=max_flops
        )
        profiles.loc[:, "mflops"] = (
            profiles.loc[:, "mflops_sp_0"] + profiles.loc[:, "mflops_dp_0"]
        )
        profiles.loc[:, "% peak performance"] = (
            profiles.loc[:, "mflops"] / profiles.loc[:, "peak performance"] * 100.0
        )

        profiling = profiles.loc[
            :,
            (
                "runtime_0",
                "memory_bandwidth_0",
                "mflops",
                "operational_intensity",
                "% peak performance",
            ),
        ]
        profiling["runtime_0"] *= 1000
        profiling = profiling.sort_values(by="runtime_0", ascending=False)

        return profiling
