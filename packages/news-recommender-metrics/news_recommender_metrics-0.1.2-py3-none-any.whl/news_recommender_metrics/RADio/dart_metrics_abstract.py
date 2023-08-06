import abc
from typing import Any, Dict

from pydantic.dataclasses import dataclass


@dataclass
class DartMetricsAbstract(abc.ABC):
    value: float
    P_dist: Dict[Any, float]
    Q_dist: Dict[Any, float]

    @abc.abstractclassmethod
    def calc(cls) -> "DartMetricsAbstract":
        raise NotImplementedError
