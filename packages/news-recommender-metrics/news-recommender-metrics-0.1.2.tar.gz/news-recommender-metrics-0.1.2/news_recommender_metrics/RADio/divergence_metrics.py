import abc
import dataclasses
import math
from collections import defaultdict
from typing import Any, Dict, List


class DivergenceMetricAbstract(abc.ABC):
    NEAR_ZERO_VALUE = 0.0001

    def calc(
        self,
        P: Dict[Any, float],
        Q: Dict[Any, float],
    ) -> float:
        """D_f(P, Q)を算出する. parametersはともに確率質量分布を想定.
        P: dictionary of probability distribution 1
        Q: dictionary of probability distribution 2
        """
        P_valid = self._convert_to_valid_dist(P, Q)
        Q_valid = self._convert_to_valid_dist(Q, P)

        divergence_P_Q = 0
        for x in P_valid.keys():
            P_x = P_valid.get(x, 0)
            Q_x = Q_valid.get(x, 0)
            divergence_P_Q += Q_x * self._function_t(P_x / Q_x)
        return divergence_P_Q

    def _convert_to_valid_dist(
        self,
        target_dist: Dict[Any, float],
        other_dist: Dict[Any, float],
    ) -> Dict[Any, float]:
        """validな確率質量分布とするための調整"""
        x_candidates = set(target_dist.keys()).union(set(other_dist.keys()))
        valid_target_dist = {}
        for x in x_candidates:
            target_prob_mass = target_dist.get(x, 0)
            other_prob_mass = other_dist.get(x, 0)
            valid_target_dist[x] = (
                1 - self.NEAR_ZERO_VALUE
            ) * target_prob_mass + self.NEAR_ZERO_VALUE * other_prob_mass
        return self._normalize(valid_target_dist)

    def _normalize(self, target_dist: Dict[Any, float]) -> Dict[Any, float]:
        """確率質量分布の性質を満たす為に、dictのvaluesの総和が1.0になるように正規化"""
        total_prob_mass = sum(target_dist.values())
        return {x: prob_mass / total_prob_mass for x, prob_mass in target_dist.items()}

    @abc.abstractmethod
    def _function_t(self, t: float) -> float:
        """f(t)の実装. 中身はdivergence metricsによって異なる."""
        raise NotImplementedError


class KLDivergence(DivergenceMetricAbstract):
    def _function_t(self, t: float) -> float:
        return t * math.log2(t)


class JSDivergence(DivergenceMetricAbstract):
    def _function_t(self, t: float) -> float:
        return 1 / 2 * ((t + 1) * math.log2(2 / (t + 1)) + t * math.log2(t))
