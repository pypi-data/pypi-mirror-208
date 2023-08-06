from collections import Counter
from typing import Any, Dict, List

from pydantic.dataclasses import dataclass


@dataclass
class ProbabilityMassFunction:
    pmf: Dict[Any, float]

    @classmethod
    def from_list(cls, R: List[Any]) -> "ProbabilityMassFunction":
        frequencies = Counter(R)
        total_count = frequencies.total()
        pmf = {x: frequency / total_count for x, frequency in frequencies.items()}
        return ProbabilityMassFunction(pmf=pmf)
