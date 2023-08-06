import dataclasses
import math
from collections import defaultdict
from typing import Any, Dict, List


@dataclasses.dataclass
class RankAwareProbabilityMassFunction:
    pmf: Dict[Any, float]

    @classmethod
    def from_ranking(
        cls, R: List[Any], method: str = "MMR"
    ) -> "RankAwareProbabilityMassFunction":
        rank_aware_pmf = defaultdict(float)
        rank_weights_sum = sum(
            [cls._calc_rank_weight(rank_idx + 1, method) for rank_idx in range(len(R))]
        )
        for rank_idx in range(len(R)):
            rank = rank_idx + 1
            rank_aware_pmf[R[rank_idx]] += (
                cls._calc_rank_weight(rank, method) / rank_weights_sum
            )
        return RankAwareProbabilityMassFunction(rank_aware_pmf)

    @classmethod
    def _calc_rank_weight(cls, rank: int, method: str = "MMR") -> float:
        if method == "MMR":
            return 1 / rank
        elif method == "nDCG":
            return 1 / (math.log2(rank + 1))
        raise ValueError("please set method arguement. (MMR/nDCG)")
