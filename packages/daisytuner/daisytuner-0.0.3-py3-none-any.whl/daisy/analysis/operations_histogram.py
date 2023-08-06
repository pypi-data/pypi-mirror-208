import ast
import json
import dace
import astunparse
import pandas as pd

from typing import Dict

from daisy.map_nest import MapNest
from daisy.analysis.analysis import Analysis


class OperationsHistogram(Analysis):
    """
    Counts the number of different operations in the map nest based on the code of the tasklets.
    The method does not take loops and branches into account.
    """

    def __init__(self, map_nest: MapNest) -> None:
        super().__init__(
            cache_path=map_nest.cache_folder / "analysis" / "operations_histogram",
            map_nest=map_nest,
        )

    def analyze(self) -> pd.Series:
        report_path = self._cache_path / "report.json"
        if report_path.is_file():
            report = json.load(open(report_path, "r"))
            report = pd.Series(report)
            return report

        report = _operations_histogram_sdfg(self._map_nest.cutout)
        self._cache_path.mkdir(exist_ok=True, parents=True)
        with open(report_path, "w") as handle:
            json.dump(report, handle)

        report = pd.Series(report)
        return report


def _operations_histogram_sdfg(sdfg: dace.SDFG) -> Dict:
    ops = {
        "+": 0,
        "-": 0,
        "*": 0,
        "/": 0,
        "logical": 0,
        "special": 0,
        "tri": 0,
    }
    for nsdfg in sdfg.all_sdfgs_recursive():
        for state in nsdfg.nodes():
            for node in state.nodes():
                if not isinstance(node, dace.nodes.Tasklet):
                    continue

                ops_tasklet = _operations_histogram_tasklet(tasklet=node)
                for key, value in ops_tasklet.items():
                    ops[key] += value

    return ops


def _operations_histogram_tasklet(tasklet: dace.nodes.Tasklet) -> Dict:
    code = tasklet.code.code

    ctr = _TaskletVisitor()
    try:
        if isinstance(code, (tuple, list)):
            for stmt in code:
                ctr.visit(stmt)
        elif isinstance(code, str):
            ctr.visit(ast.parse(code))
        else:
            ctr.visit(code)
    except SyntaxError:
        pass

    ops = {
        "+": ctr.add,
        "-": ctr.sub,
        "*": ctr.mul,
        "/": ctr.div,
        "logical": ctr.logical,
        "special": ctr.spec_funcs,
        "tri": ctr.tri_funcs,
    }

    return ops


class _TaskletVisitor(ast.NodeVisitor):
    def __init__(self):
        self.add = 0
        self.sub = 0
        self.mul = 0
        self.div = 0
        self.logical = 0
        self.spec_funcs = 0
        self.tri_funcs = 0

    def visit_Subscript(self, node: ast.Subscript):
        # Not counting index accesses as FLOP
        pass

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Add):
            self.add += 1
        elif isinstance(node.op, ast.Sub):
            self.sub += 1
        elif isinstance(node.op, ast.Mult):
            self.mul += 1
        elif isinstance(node.op, ast.Div):
            self.div += 1
        else:
            self.spec_funcs += 1

        return self.generic_visit(node)

    def visit_UnaryOp(self, node):
        if isinstance(node.op, (ast.UAdd, ast.USub)):
            self.add += 1
        elif isinstance(node.op, (ast.Not, ast.Invert)):
            self.logical += 1
        else:
            raise NotImplementedError

        return self.generic_visit(node)

    def visit_BoolOp(self, node):
        if isinstance(node.op, (ast.And, ast.Or)):
            self.logical += 1
        else:
            raise NotImplementedError

        return self.generic_visit(node)

    def visit_Compare(self, node):
        self.logical += len(node.comparators)
        return self.generic_visit(node)

    def visit_Call(self, node):
        fname = astunparse.unparse(node.func)[:-1]
        if fname in _SPECIAL_FUNCTIONS:
            self.spec_funcs += 1
        elif fname in _TRI_FUNCTIONS:
            self.tri_funcs += 1

        return self.generic_visit(node)

    def visit_AugAssign(self, node):
        return self.visit_BinOp(node)

    def visit_For(self, node):
        raise NotImplementedError

    def visit_While(self, node):
        raise NotImplementedError


_TRI_FUNCTIONS = set(
    [
        "exp",
        "pow",
        "sqrt",
        "log",
        "log2",
        "log10",
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "atan2",
        "sinh",
        "cosh",
        "tanh",
    ]
)

_SPECIAL_FUNCTIONS = set(
    [
        "min",
        "max",
        "abs",
    ]
)
