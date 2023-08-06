import json
import dace
import copy

from typing import Dict

from daisy.map_nest import MapNest
from daisy.analysis.analysis import Analysis
from daisy.analysis.soap import Solver, perform_soap_analysis


class SOAPAnalysis(Analysis):
    """
    SOAP Analysis to estimate an I/O lower bound.

    References:
        Grzegorz Kwasniewski, Tal Ben-Nun, Lukas Gianinazzi, Alexandru Calotoiu, Timo Schneider, Alexandros Nikolaos Ziogas, Maciej Besta, and Torsten Hoefler. 2021. Pebbles, Graphs, and a Pinch of Combinatorics: Towards Tight I/O Lower Bounds for Statically Analyzable Programs. In Proceedings of the 33rd ACM Symposium on Parallelism in Algorithms and Architectures (SPAA '21). Association for Computing Machinery, New York, NY, USA, 328–339. https://doi.org/10.1145/3409964.3461796
    """

    def __init__(
        self,
        map_nest: MapNest,
        address: str = "localhost",
        port: int = 30000,
    ) -> None:
        super().__init__(
            cache_path=map_nest.cache_folder / "analysis" / "soap_analysis",
            map_nest=map_nest,
        )

        self._address = address
        self._port = port
        self._solver = None

    def __del__(self):
        if self._solver is not None:
            self._solver.disconnect()

    def analyze(
        self, num_processors: int, cache_size: int, cache_only: bool = False
    ) -> Dict:
        report_path = self._cache_path / f"report_{cache_size}.json"
        if report_path.is_file():
            report = json.load(open(report_path, "r"))
            return report

        if cache_only:
            raise ValueError("Report not cached")

        self._solver = Solver(address=self._address, port=self._port)
        self._solver.connect()

        # "I" is reserved for complex numbers
        sdfg = copy.deepcopy(self._map_nest.cutout)
        sdfg.replace("I", "__I")

        bytes_per_element = 0
        for _, desc in sdfg.arrays.items():
            b = desc.dtype.bytes
            if b > bytes_per_element:
                bytes_per_element = b
        cache_size_elements = int(cache_size / bytes_per_element)

        result = perform_soap_analysis(
            sdfg=sdfg,
            solver=self._solver,
        )
        Q = result.Q

        # SOAP messes with the symbols in the SDFG, e.g., changes the case
        symbol_map = {"Ss": cache_size_elements, "p": num_processors}
        for sym in Q.free_symbols:
            if str(sym) in sdfg.constants:
                symbol_map[sym] = sdfg.constants[str(sym)]
                continue

            s = str(sym).upper()
            if s in sdfg.constants:
                symbol_map[sym] = sdfg.constants[s]

        report = {
            "Q": str(Q),
            "Q_eval": float(dace.symbolic.evaluate(Q, symbols=symbol_map)),
            "bytes_per_element": bytes_per_element,
            "symbol_map": {str(k): str(v) for k, v in symbol_map.items()},
        }

        self._cache_path.mkdir(exist_ok=True, parents=True)
        with open(report_path, "w") as handle:
            json.dump(report, handle)

        return report
