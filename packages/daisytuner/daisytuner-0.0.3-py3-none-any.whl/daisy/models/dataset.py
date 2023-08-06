import os
import json
import dace
import torch
import numpy as np
import pandas as pd

from scipy.stats import pearsonr

from functools import partial
from pathlib import Path
from tqdm import tqdm
from tabulate import tabulate
from tqdm.contrib.concurrent import process_map

from torch_geometric.data import Dataset

from daisy.utils import global_cache
from daisy.map_nest import MapNest
from daisy.analysis.profiling import Profiling
from daisy.models.encoding import Encoding


class DaisyDataset(Dataset):
    def __init__(
        self,
        root,
        transform=None,
        pre_transform=None,
        pre_filter=None,
    ):
        # self._processed_paths = list((Path(root) / "processed").rglob("*.pt"))
        self._raw_paths = list(Path(root).rglob("*.sdfg"))
        self._processed_paths = []

        super().__init__(root, transform, pre_transform, pre_filter)

    @property
    def raw_file_names(self):
        return self._raw_paths

    @property
    def processed_file_names(self):
        return self._processed_paths

    def len(self):
        return len(self._processed_paths)

    def get(self, idx):
        return torch.load(self._processed_paths[idx])

    def process(self):
        process_map(
            partial(
                process_sdfg,
                processed_dir=self.processed_dir,
            ),
            self._raw_paths,
            chunksize=2,
            max_workers=12,
        )
        # self._processed_paths = list(Path(self.processed_dir).rglob("*.pt"))

    def normalization_coefficients(self):
        archs = []
        counters = []
        targets = []
        for path in tqdm(self._processed_paths):
            data = torch.load(path).to("cpu")

            archs.append(data.arch.cpu().numpy().squeeze())
            counters.append(data.counters.cpu().numpy().squeeze())
            targets.append(data.y.cpu().numpy().squeeze())

        archs = np.vstack(archs)
        counters = np.vstack(counters)
        targets = np.vstack(targets)

        eps = 1e-6

        m = np.mean(archs, axis=0)
        s = np.std(archs, axis=0)
        archs = (archs - m) / (s + eps)
        print(np.min(archs, axis=0), np.max(archs, axis=0))

        m = np.mean(counters, axis=0)
        s = np.std(counters, axis=0)
        counters = (counters - m) / (s + eps)
        print(np.min(counters, axis=0), np.max(counters, axis=0))

        m = np.mean(targets, axis=0)
        s = np.std(targets, axis=0)
        targets = (targets - m) / (s + eps)
        print(np.min(targets, axis=0), np.max(targets, axis=0))

    @torch.inference_mode()
    def evaluate(self, model) -> None:
        sdfgs = []
        preds = []
        targets = []
        for path in tqdm(self._processed_paths):
            sdfg_name = path.stem
            data = torch.load(path).to(model.device)
            t = data.y.cpu().numpy()

            p, _, _ = model(data)
            p = p.cpu().numpy()

            preds.append(p)
            targets.append(t)
            sdfgs.append(sdfg_name)

        preds = np.vstack(preds)
        targets = np.vstack(targets)

        res = {}
        for i in range(preds.shape[1]):
            coeff, _ = pearsonr(targets[:, i], preds[:, i])
            res[self._metrics[i].replace("_", " ").title()] = coeff

            # if self._metrics[i] == "runtime":
            #     fig = px.scatter(x=targets[:, i], y=preds[:, i], hover_data=[sdfgs])
            #     fig.show()

        res = dict(sorted(res.items(), key=lambda item: item[1], reverse=False))

        # Table
        tab = tabulate(res.items(), headers=["Metric", "Pearson R"])
        print(tab)

        # # Barplot
        # sns.set_theme()
        # sns.set_context("paper")
        # sns.set_color_codes("pastel")

        # fig, ax = plt.subplots()
        # fig.set_dpi(150)
        # fig.tight_layout()
        # fig.subplots_adjust(left=0.15)

        # bars = ax.barh(y=list(res.keys()), width=list(res.values()))
        # ax.bar_label(bars, labels=[f'{x:.2f}' for x in bars.datavalues])

        # ax.set_xlim(0.2, 1.0)
        # # plt.rcParams.update({'font.size': 11})

        # plt.savefig("pearson_r.pdf", format="pdf", bbox_inches="tight")
        # plt.show()


def process_sdfg(
    sdfg_path: Path,
    processed_dir: Path,
):
    instrumentation_path = (
        sdfg_path.parent / "dacecache" / "daisy" / "analysis" / "instrumentation"
    )
    if not instrumentation_path.is_dir():
        return

    hosts = [
        Path(path).stem for path in os.scandir(instrumentation_path) if path.is_dir()
    ]

    arch_cache = {}
    for hostname in hosts:
        if not hostname in arch_cache:
            bench_path = global_cache() / f"{hostname}.json"
            with open(bench_path, "r") as handle:
                bench = json.load(handle)
                arch_cache[hostname] = bench["arch"]

        arch = arch_cache[hostname]
        if (Path(processed_dir) / f"{sdfg_path.stem}_{hostname}.pt").is_file():
            continue

        try:
            sdfg = dace.SDFG.from_file(sdfg_path)
            sdfg.build_folder = str(sdfg_path.parent / "dacecache")

            map_nest = MapNest.create(
                sdfg, state=sdfg.start_state, build_folder=sdfg.build_folder
            )
        except:
            return

        # Profiling data
        try:
            groups = GROUPS[arch]
            analysis = Profiling(
                map_nest=map_nest, hostname=hostname, arch=arch, groups=groups
            )
            _ = analysis.analyze(cache_only=True)
            metrics = analysis.performance_metrics()
        except:
            continue

        # Encoding
        try:
            encoding = Encoding(map_nest, hostname=hostname, arch=arch)
            encoding.encode(cache_only=True)
            data = encoding.torch()
        except:
            continue

        # Targets
        targets = [
            "runtime",
            "instructions_per_cycle",
            "load_to_store_ratio",
            "branch_rate",
            "branch_misprediction_ratio",
            "mflops_dp",
            "mflops_sp",
            "memory_bandwidth_0",
            "memory_bandwidth",
            "l3_bandwidth_0",
            "l3_bandwidth",
            "l2_bandwidth_0",
            "l2_bandwidth",
            "l3_request_rate",
            "l3_miss_ratio",
            "l2_request_rate",
            "l2_miss_ratio",
        ]
        target_vec = np.zeros(len(targets), dtype=np.float32)
        for i, target in enumerate(targets):
            target_vec[i] = metrics[target]

        data.y = torch.tensor(target_vec, dtype=torch.float)[None, :]
        torch.save(data, Path(processed_dir) / f"{sdfg_path.stem}_{hostname}.pt")


GROUPS = {
    "broadwellEP": [
        "MEM",
        "DATA",
        "BRANCH",
        "FLOPS_SP",
        "FLOPS_DP",
        "L3",
        "L3CACHE",
        "L2",
        "L2CACHE",
    ],
    "haswellEP": [
        "MEM",
        "DATA",
        "BRANCH",
        "FLOPS_AVX",
        "L3",
        "L3CACHE",
        "L2",
        "L2CACHE",
    ],
    "skylakeX": [
        "MEM",
        "DATA",
        "BRANCH",
        "FLOPS_SP",
        "FLOPS_DP",
        "L3",
        "L3CACHE",
        "L2",
        "L2CACHE",
    ],
    "zen": [
        "MEM",
        "DATA",
        "BRANCH",
        "FLOPS_SP",
        "FLOPS_DP",
        "L3",
        "L2",
        "CACHE",
    ],
    "zen2": [
        "MEM",
        "DATA",
        "BRANCH",
        "FLOPS_SP",
        "FLOPS_DP",
        "L3",
        "L2",
        "CACHE",
    ],
}
