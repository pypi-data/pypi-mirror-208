import copy
import dace
import numpy as np

import traceback
import multiprocessing as mp

ctx = mp.get_context("spawn")

from typing import Dict

from daisy.measure.arguments import random_arguments

from dace.codegen.compiled_sdfg import CompiledSDFG, ReloadableDLL
from dace import SDFG, config


def fuzzy_verification(
    sdfg: dace.SDFG, sdfg_: dace.SDFG, iterations: int = 1, arguments: Dict = None
) -> bool:
    for node in sdfg.start_state.data_nodes():
        if sdfg.start_state.entry_node(node) is not None:
            continue
        if (
            sdfg.start_state.in_degree(node) > 0
            and sdfg.start_state.out_degree(node) > 0
        ):
            continue
        sdfg.arrays[node.data].transient = False

    for node in sdfg_.start_state.data_nodes():
        if sdfg_.start_state.entry_node(node) is not None:
            continue
        if (
            sdfg_.start_state.in_degree(node) > 0
            and sdfg_.start_state.out_degree(node) > 0
        ):
            continue
        sdfg_.arrays[node.data].transient = False

    with config.set_temporary("compiler", "allow_view_arguments", value=True):
        sdfg_.name = sdfg.name + "_"
        sdfg_.build_folder = sdfg.build_folder + "_"
        try:
            csdfg = sdfg.compile()
            csdfg_ = sdfg_.compile()
        except:
            return False

        for _ in range(iterations):
            if arguments is None:
                arguments = random_arguments(sdfg)

            queue = ctx.Queue()
            proc = MeasureProcess(
                target=_run,
                args=(
                    sdfg.to_json(),
                    sdfg.build_folder,
                    csdfg._lib._library_filename,
                    sdfg_.to_json(),
                    sdfg_.build_folder,
                    csdfg_._lib._library_filename,
                    arguments,
                    queue,
                ),
            )
            proc.start()
            proc.join()
            if proc.is_alive():
                proc.kill()

            if proc.exitcode != 0:
                if proc.is_alive():
                    proc.kill()

                return False

            if proc.exception:
                if proc.is_alive():
                    proc.kill()

                error, traceback = proc.exception
                print(error)
                print(traceback)

                return False

            success = queue.get_nowait()

    return success


def _run(
    sdfg_json: Dict,
    build_folder: str,
    filename: str,
    sdfg_json_: Dict,
    build_folder_: str,
    filename_: str,
    arguments: Dict,
    queue: ctx.Queue,
):
    sdfg = SDFG.from_json(sdfg_json)
    sdfg.build_folder = build_folder
    lib = ReloadableDLL(filename, sdfg.name)
    csdfg = CompiledSDFG(sdfg, lib, arguments.keys())

    sdfg_ = SDFG.from_json(sdfg_json_)
    sdfg_.build_folder = build_folder_
    lib_ = ReloadableDLL(filename_, sdfg_.name)
    csdfg_ = CompiledSDFG(sdfg_, lib_, arguments.keys())

    arguments_ = copy.deepcopy(arguments)
    with config.set_temporary("compiler", "allow_view_arguments", value=True):
        csdfg(**arguments)
        csdfg_(**arguments_)

        for data in arguments:
            val = arguments[data]
            if isinstance(val, np.ndarray):
                if not np.allclose(val, arguments_[data], equal_nan=True):
                    queue.put(False)
                    return
            else:
                if not np.allclose([val], [arguments_[data]], equal_nan=True):
                    queue.put(False)
                    return

    queue.put(True)


class MeasureProcess(ctx.Process):
    def __init__(self, *args, **kwargs):
        ctx.Process.__init__(self, *args, **kwargs)
        self._pconn, self._cconn = ctx.Pipe()
        self._exception = None

    def run(self):
        try:
            ctx.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception
