import json
import re
import subprocess

from tqdm import tqdm

from daisy.utils import global_cache
from daisy.architecture import topology, architecture


class Benchmarking:
    def __init__(self, hostname: str) -> None:
        self._hostname = hostname
        self._cache_path = global_cache() / f"{hostname}.json"

    def analyze(self, cache_only: bool = False):
        if self._cache_path.is_file():
            with open(self._cache_path, "r") as handle:
                metrics = json.load(handle)
                return metrics

        if cache_only:
            raise ValueError("Benchmarking information not in cache")

        arch = architecture()["cpu"]
        topo = topology()["cpu"]

        metrics = {}
        metrics["arch"] = arch
        metrics["num_sockets"] = topo["numSockets"]
        metrics["cores_per_socket"] = topo["numCoresPerSocket"]
        metrics["threads_per_core"] = topo["numThreadsPerCore"]
        metrics["l2_cache"] = int(topo["cacheLevels"][2]["size"] / 1000)
        metrics["l3_cache"] = int(topo["cacheLevels"][3]["size"] / 1000)

        num_cpus = (
            metrics["threads_per_core"]
            * metrics["cores_per_socket"]
            * metrics["num_sockets"]
        )

        print("Executing STREAM benchmarks")
        metrics.update(Benchmarking._stream_benchmark(num_cpus))

        print("Executing peakflops benchmarks")
        metrics.update(Benchmarking._peakflops_benchmark(num_cpus))

        with open(self._cache_path, "w") as handle:
            json.dump(metrics, handle)

        return metrics

    @classmethod
    def _stream_benchmark(cls, num_cores: int):
        stream = {}
        for test in tqdm(["load", "store", "copy", "triad"]):
            process = subprocess.Popen(
                ["likwid-bench", f"-t{test}", f"-WN:2GB:{num_cores}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            stdout, stderr = process.communicate()
            res = re.findall(r"MByte/s:\t\t\d+\.\d+", stdout)
            if not res:
                raise ValueError(stderr)
            stream[f"stream_{test}"] = float(re.findall(r"\d+\.\d+", res[0])[0])

        return stream

    @classmethod
    def _peakflops_benchmark(cls, num_cores: int):
        peakflops = {}
        for name, test in tqdm(
            [("peakflops", "peakflops"), ("peakflops_avx", "peakflops_avx_fma")]
        ):
            process = subprocess.Popen(
                ["likwid-bench", f"-t{test}", f"-WN:360kB:{num_cores}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            stdout, stderr = process.communicate()
            res = re.findall(r"MFlops/s:\t\t\d+\.\d+", stdout)
            if not res:
                raise ValueError(stderr)
            peakflops[name] = float(re.findall(r"\d+\.\d+", res[0])[0])

        return peakflops
