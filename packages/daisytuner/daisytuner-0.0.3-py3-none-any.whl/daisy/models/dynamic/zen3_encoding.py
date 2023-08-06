import numpy as np
import pandas as pd

from collections import defaultdict

from daisy.map_nest import MapNest
from daisy.models.dynamic.dynamic_encoding import DynamicEncoding


class Zen3Encoding(DynamicEncoding):
    def __init__(self, map_nest: MapNest, hostname: str) -> None:
        super().__init__(map_nest=map_nest, hostname=hostname, arch="zen3")

    def _vectorize(self, data: pd.DataFrame) -> np.ndarray:
        # min, max, sum, mean, std
        num_statistics = 5
        num_counters = 16

        encoding = np.zeros((num_statistics * num_counters,))

        # Total instructions
        encoding[0 * num_statistics : 1 * num_statistics] = DynamicEncoding._normalize(
            data, "RETIRED_INSTRUCTIONS"
        )

        # FLOPS_SP
        encoding[1 * num_statistics : 2 * num_statistics] = DynamicEncoding._normalize(
            data, "RETIRED_SSE_AVX_FLOPS_ALL"
        )
        encoding[2 * num_statistics : 5 * num_statistics] = 0.0

        # FLOPS_DP
        encoding[5 * num_statistics : 6 * num_statistics] = DynamicEncoding._normalize(
            data, "RETIRED_SSE_AVX_FLOPS_ALL"
        )
        encoding[6 * num_statistics : 9 * num_statistics] = 0.0

        # BRANCH
        encoding[9 * num_statistics : 10 * num_statistics] = DynamicEncoding._normalize(
            data, "RETIRED_BRANCH_INSTR"
        )
        encoding[
            10 * num_statistics : 11 * num_statistics
        ] = DynamicEncoding._normalize(data, "RETIRED_MISP_BRANCH_INSTR")

        # MEM Volume
        encoding[11 * num_statistics : 12 * num_statistics] = (
            DynamicEncoding._normalize(data, "DRAM_CHANNEL_0")
            + DynamicEncoding._normalize(data, "DRAM_CHANNEL_1")
            + DynamicEncoding._normalize(data, "DRAM_CHANNEL_2")
            + DynamicEncoding._normalize(data, "DRAM_CHANNEL_3")
            + DynamicEncoding._normalize(data, "DRAM_CHANNEL_4")
            + DynamicEncoding._normalize(data, "DRAM_CHANNEL_5")
            + DynamicEncoding._normalize(data, "DRAM_CHANNEL_6")
            + DynamicEncoding._normalize(data, "DRAM_CHANNEL_7")
        )

        # L3 Volume
        encoding[12 * num_statistics : 13 * num_statistics] = (
            DynamicEncoding._normalize(data, "L2_PF_HIT_IN_L3")
            + DynamicEncoding._normalize(data, "L2_PF_MISS_IN_L3")
            + DynamicEncoding._normalize(data, "L2_CACHE_MISS_AFTER_L1_MISS")
        )

        # L2 Volume
        encoding[
            13 * num_statistics : 14 * num_statistics
        ] = DynamicEncoding._normalize(
            data, "REQUESTS_TO_L2_GRP1_ALL_NO_PF"
        ) + DynamicEncoding._normalize(
            data, "L2_PF_HIT_IN_L2"
        )

        # DRAM Controller
        encoding[
            14 * num_statistics : 15 * num_statistics
        ] = DynamicEncoding._normalize(
            data, "LS_DISPATCH_LOADS"
        ) + DynamicEncoding._normalize(
            data, "LS_DISPATCH_LOAD_OP_STORES"
        )
        encoding[
            15 * num_statistics : 16 * num_statistics
        ] = DynamicEncoding._normalize(
            data, "LS_DISPATCH_STORES"
        ) + DynamicEncoding._normalize(
            data, "LS_DISPATCH_LOAD_OP_STORES"
        )

        return encoding
