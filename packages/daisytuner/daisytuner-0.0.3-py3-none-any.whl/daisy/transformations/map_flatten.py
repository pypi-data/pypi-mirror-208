import dace

from dace.sdfg import SDFG
from dace.sdfg import nodes
from dace.sdfg import utils as sdutil
from dace.sdfg.state import SDFGState
from dace.transformation import transformation
from dace.properties import make_properties, Property, EnumProperty


@make_properties
class MapFlatten(transformation.SingleStateTransformation):
    map_entry = transformation.PatternNode(nodes.MapEntry)

    @classmethod
    def expressions(cls):
        return [sdutil.node_path_graph(cls.map_entry)]

    def can_be_applied(self, state, expr_index, sdfg, permissive=False):
        if len(self.map_entry.params) <= 2:
            return False

        flattened_ranges = self.map_entry.map.range[:2]
        b0, e0, s0 = flattened_ranges[0]
        b1, e1, s1 = flattened_ranges[1]
        if b1 != 0 or b0 != 0:
            return False
        if s0 != 1 or s1 != 1:
            return False

        return True

    def apply(self, state: SDFGState, sdfg: SDFG):
        params = self.map_entry.map.params
        flattened_params = params[:2]
        flattened_ranges = self.map_entry.map.range[:2]

        new_param = "__i0"
        i = 0
        while new_param in params:
            i = i + 1
            new_param = f"__i{i}"

        _, e0, _ = flattened_ranges[0]
        e0 = e0 + 1
        _, e1, _ = flattened_ranges[1]
        e1 = e1 + 1

        flattened_range = 0, (e0 * e1) - 1, 1

        self.map_entry.map.params = [new_param] + params[2:]
        self.map_entry.map.range = dace.subsets.Range(
            [flattened_range] + self.map_entry.map.range[2:]
        )

        map_scope = state.scope_subgraph(
            self.map_entry, include_entry=True, include_exit=True
        )

        new_param_sym = dace.symbolic.symbol(new_param)
        repl1 = dace.symbolic.int_floor(new_param_sym, e1)
        repl2 = new_param_sym % e1
        map_scope.replace(flattened_params[0], str(repl1))
        map_scope.replace(flattened_params[1], str(repl2))
