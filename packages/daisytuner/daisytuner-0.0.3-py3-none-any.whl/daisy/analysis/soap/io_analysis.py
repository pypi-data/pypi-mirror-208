import sympy as sp
import networkx as nx

from typing import Dict, List, Union, Set
from dataclasses import dataclass, field

from dace import SDFG, Config
from dace.sdfg.graph import SubgraphView
from daisy.analysis.soap.sdg import SDG
from daisy.analysis.soap.solver import Solver
from daisy.analysis.soap.einsum_to_sdfg import sdfg_gen


@dataclass
class IOAnalysisSubgraph:
    name: int
    Q: sp.Expr
    rho: sp.Expr
    input_arrays: Dict
    tasklets: Set
    variables: List[sp.Expr]
    inner_tile: List[sp.Expr]
    outer_tile: List[sp.Expr]

    # The following three fields define the parallel distribution.
    # they require user to specify numerical value of parameters,
    # such as P, S, and problem sizes. The default values of some of these
    # parameters are specified in utils.param_values
    loc_domain_dims: List[sp.Expr] = field(default_factory=list)
    p_grid: List[sp.Expr] = field(default_factory=list)
    dimensions_ordered: List[sp.Expr] = field(default_factory=list)

    def get_data_decomposition(self, pp):
        # p_pos is an N -> N^d mapping, translating a global rank to a cooridnate rank in
        # the d-dimensional iteration space  (p  -> [p_x, p_y, p_z, ....])
        if sp.prod(self.p_grid) <= pp:
            print(
                "\n\nDecomposition uses only {} processors. Given rank {} will be idle!\n\n".format(
                    sp.prod(self.p_grid), pp
                )
            )
            return {}

        div = lambda x, y: (x - x % y) / y
        p_pos = []
        for dim_num, dim_size in enumerate(self.p_grid):
            p_dim = div(pp, sp.prod(self.p_grid[dim_num + 1 :]))
            p_pos.append(p_dim)
            pp -= p_dim * sp.prod(self.p_grid[dim_num + 1 :])

        iter_ranges = {
            str(var): (
                p_pos[i] * self.loc_domain_dims[i],
                min((p_pos[i] + 1) * self.loc_domain_dims[i], dim_size),
            )
            for i, (var, dim_size) in enumerate(
                zip(self.variables, self.dimensions_ordered)
            )
        }

        par_distribution = {}
        for arr, accesses in self.input_arrays.items():
            for access, pars in accesses.items():
                rngs = {}
                for it in access.split("*"):
                    rngs[it] = iter_ranges[it]
            par_distribution[arr] = rngs

        return par_distribution


@dataclass
class IOAnalysis:
    name: int
    Q: sp.Expr
    sdg: SDG
    subgraphs: List[IOAnalysisSubgraph]


def perform_soap_analysis(
    solver: Solver,
    sdfg: Union[SDFG, SubgraphView],
) -> IOAnalysis:
    """
    Main interface of the SOAP analysis.

    Input:
    sdfg (SDFG): sdfg to be analyzed
    generate_schedule [Optional] (bool): Whether the parallel decomposition should be evaluated for each subgraph. The decomposition parameters are specified in params.param_values. decomp_params: specifies numerical values of the symbolic parameters as a list of tuples (e.g., [("p", 64, "Ss", 1024, "N", 128)]).

    Output:
    io_result_subgraph: dataclass containing SOAP analysis results,
    such as I/O lower bound (Q), computational intensity (rho), symbolic directed graph (SDG),
    and the list of subgraphs (subgraphs) with their optimal tilings and kernel merging
    """
    sdg = SDG(sdfg, solver)
    # check if the created SDG is correct
    assert nx.number_weakly_connected_components(sdg.graph) == 1
    Q, subgraphs = sdg.calculate_IO_of_SDG()

    subgraphs_res = []
    for subgr in subgraphs:
        io_res_sg = IOAnalysisSubgraph(
            name=subgr.name,
            Q=subgr.Q,
            rho=subgr.rhoOpts,
            variables=subgr.variables,
            inner_tile=subgr.inner_tile,
            outer_tile=subgr.outer_tile,
            input_arrays=subgr.phis,
            tasklets=subgr.tasklet,
        )
        subgraphs_res.append(io_res_sg)

    return IOAnalysis(SDFG.__name__, Q, sdg, subgraphs_res)
