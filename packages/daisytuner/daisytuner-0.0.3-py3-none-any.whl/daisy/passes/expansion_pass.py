import dace

from typing import Any, Dict, List

from dace.transformation import pass_pipeline as ppl


class ExpansionPass(ppl.Pass):
    """
    Expands library nodes of an SDFG with implementations according to an order of implementations.
    """

    CATEGORY: str = "Simplification"

    recursive = True
    order: List[str] = ["MKL", "pure"]

    def __init__(self, order: List[str] = ["MKL", "pure"]) -> None:
        super().__init__()

        self.order = order

    def modifies(self) -> ppl.Modifies:
        return ppl.Modifies.Everything

    def should_reapply(self, modified: ppl.Modifies) -> bool:
        return False

    def apply_pass(self, sdfg: dace.SDFG, pipeline_results: Dict[str, Any]) -> int:
        expanded = 0

        states = list(sdfg.states())
        while len(states) > 0:
            state = states.pop()
            expanded_something = False

            nodes = list(state.nodes())
            while nodes:
                node = nodes.pop()

                if isinstance(node, dace.nodes.LibraryNode):
                    if isinstance(node, dace.nodes.UnregisteredLibraryNode):
                        continue

                    if set(self.order).isdisjoint(set(node.implementations.keys())):
                        _ = node.expand(sdfg, state)
                        expanded_something = True
                        expanded += 1
                        continue
                    else:
                        for impl in self.order:
                            if impl in node.implementations.keys():
                                node.implementation = impl

                                try:
                                    _ = node.expand(sdfg, state)
                                    expanded_something = True
                                    expanded += 1
                                    break
                                except:
                                    continue

            if expanded_something:
                states.append(state)

        return expanded
