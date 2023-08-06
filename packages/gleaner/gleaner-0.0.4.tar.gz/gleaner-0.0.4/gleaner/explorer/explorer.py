from typing import TYPE_CHECKING

from dataclasses import dataclass
from collections import Counter
import pandas as pd
import numpy as np
from gleaner.explorer import TrainResult

from gleaner.oracle import Oracle, OracleResult
from gleaner.model import GleanerChart, GleanerDashboard
from gleaner.config import GleanerConfig

from gleaner.generator import Generator


def mean(l):
    return sum(l) / len(l)


class PosteriorCounter(Counter):
    def __init__(self, names):
        super().__init__({n: 0 for n in names})

    def get_posteriors(self, names: list):
        return np.array([self[n] for n in names])


class Counters:
    def __init__(self, attr_names):
        self.attr_names = attr_names
        self.x = PosteriorCounter(attr_names)
        self.y = PosteriorCounter(attr_names)
        self.z = PosteriorCounter(attr_names)
        self.ct = PosteriorCounter(attr_names)
        self.at = PosteriorCounter(attr_names)

    def update(self, node: GleanerChart):
        ct, x, y, z, at = node.sample
        self.ct[ct] += 1
        self.x[x] += 1
        self.y[y] += 1
        self.z[z] += 1
        self.at[at] += 1


class Explorer:
    config: GleanerConfig
    df: pd.DataFrame
    dashboard: GleanerDashboard | None = None
    result: OracleResult | None = None

    def __init__(self, df: pd.DataFrame, config: GleanerConfig) -> None:
        self.df = df
        self.config = config

    def _infer(
        self,
        gen: Generator,
        oracle: Oracle,
        preferences: list[str],
        n_chart: int | None = None,
        fixed_charts: list[GleanerChart] = [],
    ):
        if n_chart and n_chart < len(fixed_charts):
            raise ValueError("Number of fixed_charts should be smaller than n_chart")

        n_charts: list[float] = [
            gen.prior.n_charts.sample() if n_chart is None else n_chart for _ in range(self.config.n_candidates)
        ]

        if len(fixed_charts):
            n_charts = [max(1, n - len(fixed_charts)) for n in n_charts]

        candidates: list[GleanerDashboard] = [gen.sample_dashboard(round(n_chart)) for n_chart in n_charts]

        if len(fixed_charts):
            for candidate in candidates:
                candidate.extend(fixed_charts)

        results: list[OracleResult] = [oracle.get_result(dashboard, set(preferences)) for dashboard in candidates]

        specificity = np.array([r.specificity for r in results])
        interestingness = np.array([r.interestingness for r in results])
        coverage = np.array([r.coverage for r in results])
        diversity = np.array([r.diversity for r in results])
        conciseness = np.array([r.conciseness for r in results])

        raw_scores: np.ndarray = (
            specificity * oracle.weight.specificity
            + interestingness * oracle.weight.interestingness
            + coverage * oracle.weight.coverage
            + diversity * oracle.weight.diversity
            + conciseness * oracle.weight.conciseness
        )

        normalized_scores = (
            (
                0
                if len(preferences) == 0
                else (specificity - specificity.mean()) / specificity.std() * oracle.weight.specificity
            )
            + (interestingness - interestingness.mean()) / interestingness.std() * oracle.weight.interestingness
            + (coverage - coverage.mean()) / coverage.std() * oracle.weight.coverage
            + (diversity - diversity.mean()) / diversity.std() * oracle.weight.diversity
            + (conciseness - conciseness.mean()) / conciseness.std() * oracle.weight.conciseness
        )

        result_n_scores: list[tuple[OracleResult, GleanerDashboard, float, float]] = [
            (result, candidates[i], raw_scores[i], normalized_scores[i]) for i, result in enumerate(results)
        ]

        result_n_scores.sort(key=lambda x: x[-1], reverse=True)

        return (
            result_n_scores,
            raw_scores,
            normalized_scores,
            specificity,
            interestingness,
            coverage,
            diversity,
            conciseness,
        )

    def infer(
        self,
        gen: Generator,
        oracle: Oracle,
        preferences: list[str],
        n_chart: int | None = None,
        fixed_charts: list[list[str | None]] = [],
    ) -> GleanerDashboard:
        (
            result_n_scores,
            raw_scores,
            normalized_scores,
            specificity,
            interestingness,
            coverage,
            diversity,
            conciseness,
        ) = self._infer(gen, oracle, preferences, n_chart, [GleanerChart(c, self.df) for c in fixed_charts])

        return result_n_scores[0][1]

    def _train(self, gen: Generator, oracle: Oracle, preferences: list[str]) -> TrainResult:
        (
            result_n_scores,
            raw_scores,
            normalized_scores,
            specificity,
            interestingness,
            coverage,
            diversity,
            conciseness,
        ) = self._infer(gen, oracle, preferences)

        expl_idx = np.argmax(normalized_scores)
        if self.result is None or raw_scores[expl_idx] < self.result.get_score():
            self.dashboard = result_n_scores[expl_idx][1]
            self.result = result_n_scores[expl_idx][0]

        result_n_scores = sorted(result_n_scores, key=lambda x: x[-1], reverse=True)

        halved_results = result_n_scores[0 : int(self.config.n_candidates * self.config.halving_ratio)]
        halved_n_charts = np.array([len(r[1]) for r in halved_results])

        none_attr_names: list[str | None] = [None, *self.config.attr_names]
        counters = Counters(none_attr_names)
        for candidate in halved_results:
            charts = candidate[1].charts
            for chart in charts:
                counters.update(chart)

        gen.prior.x.update(counters.x.get_posteriors(none_attr_names))
        gen.prior.y.update(counters.y.get_posteriors(none_attr_names))
        gen.prior.z.update(counters.z.get_posteriors(none_attr_names))
        gen.prior.ct.update(counters.ct.get_posteriors(self.config.chart_type))
        gen.prior.at.update(counters.at.get_posteriors(self.config.agg_type))
        gen.prior.n_charts.update(len(halved_n_charts), halved_n_charts.mean(), halved_n_charts.std())

        return TrainResult(
            raw_scores,
            specificity,
            interestingness,
            coverage,
            diversity,
            conciseness,
            np.array([len(d[1]) for d in result_n_scores]),
        )

    def train(self, gen: Generator, oracle: Oracle, preferences: list[str]) -> list[TrainResult]:
        results = []
        for _ in range(self.config.n_epoch):
            results.append(self._train(gen, oracle, preferences))
        return results
