import copy
import dace

from dace.libraries.blas.nodes import Gemm
from dace.libraries.blas.nodes.matmul import _get_matmul_operands

from dace.sdfg import utils as sdutil
from dace.transformation import transformation
from dace.properties import make_properties, Property


@make_properties
class Sparsify(transformation.SingleStateTransformation):
    libary_node = transformation.PatternNode(dace.nodes.LibraryNode)

    swap_arguments = Property(dtype=bool, default=False)

    @classmethod
    def expressions(cls):
        return [sdutil.node_path_graph(cls.libary_node)]

    def can_be_applied(
        self,
        state: dace.SDFGState,
        expr_index: int,
        sdfg: dace.SDFG,
        permissive: bool = False,
    ):
        if not isinstance(self.libary_node, Gemm):
            return False

        (edge_a, desc_a, shape_a, strides_a), b, c = _get_matmul_operands(
            self.libary_node, state, sdfg
        )
        name_a = edge_a.src.data
        # A must be a source node
        if state.in_degree(edge_a.src) > 0 and not desc_a.transient:
            return False

        # A must be read completely
        ref_memlet = dace.Memlet.from_array(edge_a.data.data, desc_a)
        if not edge_a.data.subset.covers(ref_memlet.subset):
            return False

        nsdfg = sdfg
        parent_sdfg = sdfg.parent_sdfg
        replace_name = name_a
        while parent_sdfg is not None:
            nested_node = nsdfg.parent_nsdfg_node
            parent_state = None
            for s in parent_sdfg.states():
                if nested_node in s.nodes():
                    parent_state = s
                    break

            edges = list(parent_state.in_edges_by_connector(nested_node, replace_name))
            if len(edges) > 1:
                return False

            for edge in edges:
                desc = parent_sdfg.arrays[edge.src.data]
                if parent_state.in_degree(edge.src) > 0 and not desc.transient:
                    return False

                # A must be read completely
                ref_memlet = dace.Memlet.from_array(edge.src.data, desc)
                if not edge.data.subset.covers(ref_memlet.subset):
                    return False

            replace_name = edge.src.data
            nsdfg = parent_sdfg
            parent_sdfg = parent_sdfg.parent_sdfg

        return True

    def apply(self, state: dace.SDFGState, sdfg: dace.SDFG):
        if self.swap_arguments:
            # Yes
            self.libary_node.transA = not self.libary_node.transA

            # Not necessary; explicit transpose map
            # self.libary_node.transB = not self.libary_node.transB

            edge_a = state.in_edges_by_connector(self.libary_node, "_a")
            edge_a = next(edge_a.__iter__())
            array_a = edge_a.data.data
            desc_a = sdfg.arrays[array_a]
            state.remove_edge(edge_a)

            edge_b = state.in_edges_by_connector(self.libary_node, "_b")
            edge_b = next(edge_b.__iter__())
            state.remove_edge(edge_b)

            edge_c = state.out_edges_by_connector(self.libary_node, "_c")
            edge_c = next(edge_c.__iter__())
            array_c = edge_c.data.data
            desc_c = sdfg.arrays[array_c]
            state.remove_edge(edge_c)

            state.add_edge(
                edge_b.src,
                edge_b.src_conn,
                self.libary_node,
                "_a",
                copy.deepcopy(edge_b.data),
            )
            """
            state.add_edge(
                edge_a.src,
                edge_a.src_conn,
                self.libary_node,
                "_b",
                copy.deepcopy(edge_a.data),
            )
            """

            array_a_trans = array_a + "_trans"
            array_a_trans, desc_a_trans = sdfg.add_array(
                array_a_trans,
                desc_a.shape[::-1],
                desc_a.dtype,
                storage=desc_a.storage,
                transient=True,
                find_new_name=True,
            )

            trans_access_node_a = state.add_access(array_a_trans)
            state.add_edge(
                trans_access_node_a,
                None,
                self.libary_node,
                "_b",
                dace.Memlet.from_array(array_a_trans, desc_a_trans),
            )

            _, map_entry, map_exit = state.add_mapped_tasklet(
                "transpose",
                {f"_i{i}": f"0:{d}" for i, d in enumerate(desc_a.shape)},
                {
                    "_in": dace.Memlet.simple(
                        array_a,
                        ",".join([f"_i{i}" for i in range(len(desc_a.shape))]),
                    )
                },
                "_out = _in",
                {
                    "_out": dace.Memlet.simple(
                        array_a_trans,
                        ",".join(
                            [
                                f"_i{i}"
                                for i in range(len(desc_a_trans.shape) - 1, -1, -1)
                            ]
                        ),
                    )
                },
            )

            state.add_edge(
                edge_a.src,
                None,
                map_entry,
                None,
                dace.Memlet.from_array(array_a, desc_a),
            )
            state.add_edge(
                map_exit,
                None,
                trans_access_node_a,
                None,
                dace.Memlet.from_array(array_a_trans, desc_a_trans),
            )

            array_c_trans = array_c + "_trans"
            array_c_trans, desc_c_trans = sdfg.add_array(
                array_c_trans,
                desc_c.shape[::-1],
                desc_c.dtype,
                storage=desc_c.storage,
                transient=True,
                find_new_name=True,
            )

            trans_access_node = state.add_access(array_c_trans)
            state.add_edge(
                self.libary_node,
                edge_c.src_conn,
                trans_access_node,
                None,
                dace.Memlet.from_array(array_c_trans, desc_c_trans),
            )

            _, map_entry, map_exit = state.add_mapped_tasklet(
                "transpose",
                {f"_i{i}": f"0:{d}" for i, d in enumerate(desc_c_trans.shape)},
                {
                    "_in": dace.Memlet.simple(
                        array_c_trans,
                        ",".join([f"_i{i}" for i in range(len(desc_c_trans.shape))]),
                    )
                },
                "_out = _in",
                {
                    "_out": dace.Memlet.simple(
                        array_c,
                        ",".join(
                            [f"_i{i}" for i in range(len(desc_c.shape) - 1, -1, -1)]
                        ),
                    )
                },
            )

            state.add_edge(
                trans_access_node,
                None,
                map_entry,
                None,
                dace.Memlet.from_array(array_c_trans, desc_c_trans),
            )
            state.add_edge(
                map_exit,
                None,
                edge_c.dst,
                None,
                dace.Memlet.from_array(array_c, desc_c),
            )

            sdfg.fill_scope_connectors()
            dace.propagate_memlets_sdfg(sdfg)

        from dace.libraries.sparse.nodes import CSRMM

        (
            (edge_a, desc_a, _, _),
            (edge_b, desc_b, _, _),
            (edge_c, desc_c, _, _),
        ) = _get_matmul_operands(self.libary_node, state, sdfg)
        name_a = edge_a.src.data
        if isinstance(desc_a, dace.data.View):
            name_a = state.in_edges(edge_a.src)[0].src.data

        # Replace in parent SDFGs
        nsdfg = sdfg
        parent_sdfg = sdfg.parent_sdfg
        replace_name = name_a
        while parent_sdfg is not None:
            nested_node = nsdfg.parent_nsdfg_node
            parent_state = None
            for s in parent_sdfg.states():
                if nested_node in s.nodes():
                    parent_state = s
                    break

            edge = next(
                parent_state.edges_by_connector(nested_node, replace_name).__iter__()
            )
            parent_state.remove_edge_and_connectors(edge)
            parent_state.remove_node(edge.src)

            nested_node.add_in_connector(replace_name + "_val")
            nested_node.add_in_connector(replace_name + "_col")
            nested_node.add_in_connector(replace_name + "_row")

            a_nnz = dace.symbolic.symbol(edge.src.data + "_nnz", dtype=dace.int64)
            parent_sdfg.add_symbol(edge.src.data + "_nnz", dace.int64)
            nested_node.symbol_mapping[replace_name + "_nnz"] = edge.src.data + "_nnz"

            a_vals, a_vals_desc = parent_sdfg.add_array(
                edge.src.data + "_val",
                shape=(a_nnz,),
                dtype=desc_a.dtype,
                transient=False,
                storage=desc_a.storage,
            )
            a_vals_node = parent_state.add_read(edge.src.data + "_val")
            parent_state.add_edge(
                a_vals_node,
                None,
                nested_node,
                replace_name + "_val",
                dace.Memlet.from_array(a_vals, a_vals_desc),
            )

            a_cols, a_cols_desc = parent_sdfg.add_array(
                edge.src.data + "_col",
                shape=(a_nnz,),
                dtype=dace.int32,
                transient=False,
                storage=desc_a.storage,
            )
            a_cols_node = parent_state.add_read(edge.src.data + "_col")
            parent_state.add_edge(
                a_cols_node,
                None,
                nested_node,
                replace_name + "_col",
                dace.Memlet.from_array(a_cols, a_cols_desc),
            )

            a_rows, a_rows_desc = parent_sdfg.add_array(
                edge.src.data + "_row",
                shape=(desc_a.shape[0] + 1,),
                dtype=dace.int32,
                transient=False,
                storage=desc_a.storage,
            )
            a_rows_node = parent_state.add_read(edge.src.data + "_row")
            parent_state.add_edge(
                a_rows_node,
                None,
                nested_node,
                replace_name + "_row",
                dace.Memlet.from_array(a_rows, a_rows_desc),
            )

            parent_sdfg.arg_names.append(edge.src.data + "_val")
            parent_sdfg.arg_names.append(edge.src.data + "_col")
            parent_sdfg.arg_names.append(edge.src.data + "_row")

            remove_A = True
            for s in parent_sdfg.states():
                for dnode in s.data_nodes():
                    if dnode.data == edge.src.data:
                        remove_A = False
                        break

            if remove_A:
                parent_sdfg.remove_data(edge.src.data)
                if edge.src.data in parent_sdfg.arg_names:
                    parent_sdfg.arg_names.remove(edge.src.data)

            replace_name = edge.src.data
            nsdfg = parent_sdfg
            parent_sdfg = parent_sdfg.parent_sdfg

        # Add CSR arrays to current SDFG
        sdfg.add_symbol(name_a + "_nnz", dace.int64)
        a_nnz = dace.symbolic.symbol(name_a + "_nnz", dtype=dace.int64)

        a_vals, a_vals_desc = sdfg.add_array(
            name_a + "_val",
            shape=(a_nnz,),
            dtype=desc_a.dtype,
            transient=False,
            storage=desc_a.storage,
        )
        a_vals_node = state.add_read(name_a + "_val")

        a_cols, a_cols_desc = sdfg.add_array(
            name_a + "_col",
            shape=(a_nnz,),
            dtype=dace.int32,
            transient=False,
            storage=desc_a.storage,
        )
        a_cols_node = state.add_read(name_a + "_col")

        a_num_rows = (
            (desc_a.shape[0] + 1,)
            if not self.libary_node.transA
            else (desc_a.shape[1] + 1,)
        )
        a_rows, a_rows_desc = sdfg.add_array(
            name_a + "_row",
            shape=a_num_rows,
            dtype=dace.int32,
            transient=False,
            storage=desc_a.storage,
        )
        a_rows_node = state.add_read(name_a + "_row")

        sdfg.arg_names.append(name_a + "_val")
        sdfg.arg_names.append(name_a + "_col")
        sdfg.arg_names.append(name_a + "_row")

        # Add sparse node
        sparse_node = CSRMM(
            "CSRMM",
            alpha=self.libary_node.alpha,
            beta=self.libary_node.beta,
            transB=self.libary_node.transB,
        )
        sparse_node.implementation = "pure"

        # Connect new sparse node
        state.add_edge(
            a_vals_node,
            None,
            sparse_node,
            "_a_vals",
            dace.Memlet.from_array(a_vals, a_vals_desc),
        )
        state.add_edge(
            a_rows_node,
            None,
            sparse_node,
            "_a_rows",
            dace.Memlet.from_array(a_rows, a_rows_desc),
        )
        state.add_edge(
            a_cols_node,
            None,
            sparse_node,
            "_a_cols",
            dace.Memlet.from_array(a_cols, a_cols_desc),
        )
        state.add_edge(
            edge_b.src, edge_b.src_conn, sparse_node, "_b", copy.deepcopy(edge_b.data)
        )
        state.add_edge(
            sparse_node, "_c", edge_c.dst, edge_c.dst_conn, copy.deepcopy(edge_c.data)
        )

        if "_cin" in self.libary_node.in_connectors:
            edge_cin = next(
                state.edges_by_connector(self.libary_node, "_cin").__iter__()
            )
            state.add_edge(
                edge_cin.src,
                edge_cin.src_conn,
                sparse_node,
                "_cin",
                copy.deepcopy(edge_cin.data),
            )

        # Cleanup
        state.remove_edge_and_connectors(edge_a)
        state.remove_edge_and_connectors(edge_b)
        state.remove_edge_and_connectors(edge_c)
        if "_cin" in self.libary_node.in_connectors:
            for edge in state.edges_by_connector(self.libary_node, "_cin"):
                state.remove_edge(edge)

        state.remove_node(self.libary_node)

        if state.out_degree(edge_a.src) == 0:
            # TODO: Recursive
            for edge in state.in_edges(edge_a.src):
                state.remove_edge(edge)
                state.remove_node(edge.src)

            state.remove_node(edge_a.src)

            remove_array = True
            for s in sdfg.states():
                for dnode in s.data_nodes():
                    if dnode.data == name_a:
                        remove_array = False
                        break

            if remove_array:
                sdfg.remove_data(name_a)
                if name_a in sdfg.arg_names:
                    sdfg.arg_names.remove(name_a)
