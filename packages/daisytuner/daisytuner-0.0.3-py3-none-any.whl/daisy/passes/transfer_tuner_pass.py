import dace

from dace.transformation import pass_pipeline as ppl
from dataclasses import dataclass
from typing import Any, Dict

from daisy.map_nest import MapNest
from daisy.tuner import TransferTuner


@dace.properties.make_properties
class TransferTunerPass(ppl.ScopePass):
    """
    Transfer tunes the map nests of the SDFG. If no hostname is provided, the search falls back to an architecture-agnostic embeddings.
    """

    CATEGORY: str = "Optimization"

    def __init__(self, hostname: str = None, arch: str = None, topK: int = 3) -> None:
        super().__init__()

        self._hostname = hostname
        self._arch = arch
        self._topK = topK
        self._tuner = TransferTuner(hostname=self._hostname, arch=self._arch)

    def modifies(self) -> ppl.Modifies:
        return ppl.Modifies.Scopes

    def should_reapply(self, modified: ppl.Modifies) -> bool:
        return False

    def apply(
        self,
        scope: dace.nodes.EntryNode,
        state: dace.SDFGState,
        pipeline_results: Dict[str, Any],
    ) -> int:
        if (
            not isinstance(scope, dace.nodes.MapEntry)
            or state.entry_node(scope) is not None
        ):
            return None

        map_nest = MapNest.create(state.parent, state, scope)

        # Filter init maps
        has_input = False
        for node in map_nest.cutout.start_state.data_nodes():
            if map_nest.cutout.start_state.in_degree(node) == 0:
                has_input = True

        if not has_input:
            return None

        schedule = self._tuner.tune(map_nest=map_nest, topK=self._topK)
        return schedule
