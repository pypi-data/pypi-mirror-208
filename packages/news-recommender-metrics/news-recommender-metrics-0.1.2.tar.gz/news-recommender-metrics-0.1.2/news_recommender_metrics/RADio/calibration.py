from typing import Any, Dict, List

from pydantic.dataclasses import dataclass

from news_recommender_metrics.RADio.dart_metrics_abstract import DartMetricsAbstract
from news_recommender_metrics.RADio.divergence_metrics import (
    DivergenceMetricAbstract,
    JSDivergence,
)
from news_recommender_metrics.utils.probability_mass_function.probability_mass_function import (
    ProbabilityMassFunction,
)
from news_recommender_metrics.utils.probability_mass_function.rank_aware_probability_mass_function import (
    RankAwareProbabilityMassFunction,
)


@dataclass
class Calibration(DartMetricsAbstract):
    value: float
    P_dist: Dict[Any, float]
    Q_dist: Dict[Any, float]

    @classmethod
    def calc(
        cls,
        reading_history: List[Any],
        recommendations: List[Any],
        is_rank_aware: bool = True,
        rank_weight_method: str = "MMR",
    ) -> "Calibration":
        """_summary_

        Parameters
        ----------
        reading_history : List[Any]
            the user's reading history of news. element is an item attribute for calculate Calibration.(ex. news category label)
        recommendations : List[Any]
            recommendation result for the user. it's assumed being sorted by recommendation ranking.
        is_rank_aware : bool
            if True, calculate Calibration with rank-aware distribution of recommendations.
            Else, calculate without considering ranking.
        rank_weight_method: str = "MMR"
            the method for weighting of the rank.("MMR" or "nDCG")
        Returns
        -------
        Calibration
            Calibration of the item attribute.
        """

        P_dist = ProbabilityMassFunction.from_list(reading_history)

        Q_dist = (
            RankAwareProbabilityMassFunction.from_ranking(
                recommendations, rank_weight_method
            )
            if is_rank_aware
            else ProbabilityMassFunction.from_list(recommendations)
        )
        calculator = JSDivergence()
        value = calculator.calc(P_dist.pmf, Q_dist.pmf)

        return Calibration(
            value=value,
            P_dist=P_dist.pmf,
            Q_dist=Q_dist.pmf,
        )
