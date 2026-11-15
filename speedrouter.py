# SpeedRouter - Route inputs to experts by estimated difficulty
# Part of the Kapildhinwa2010-dev Toolkit.

"""RouterNet - complexity-based request routing.

Lineage: DNA_DYNIMO routers. Requests are scored for complexity (norm,
entropy proxy, length) and routed to the cheapest expert whose capacity
threshold covers the score, saving compute on easy inputs.
"""

from __future__ import annotations

import numpy as np

__all__ = ["complexity_score", "Expert", "ComplexityRouter"]


def complexity_score(vector: np.ndarray) -> float:
    """Composite complexity: L2 norm + normalized entropy of |v|/sum|v|."""
    vector = np.asarray(vector, dtype=np.float64).ravel()
    if vector.size == 0:
        raise ValueError("vector must be non-empty")
    norm = float(np.linalg.norm(vector))
    magnitudes = np.abs(vector)
    total = magnitudes.sum()
    if total <= 0:
        return 0.0
    probs = magnitudes / total
    probs = probs[probs > 0]
    entropy = float(-(probs * np.log(probs)).sum() / np.log(vector.size))
    return norm * (0.5 + 0.5 * entropy)


class Expert:
    """One routing target with a capacity threshold and call counter."""

    def __init__(self, name: str, capacity: float, cost: float = 1.0) -> None:
        if not name:
            raise ValueError("name must be non-empty")
        if capacity <= 0 or cost < 0:
            raise ValueError("capacity must be > 0 and cost >= 0")
        self.name = name
        self.capacity = float(capacity)
        self.cost = float(cost)
        self.calls = 0

    def handle(self, score: float) -> str:
        if score > self.capacity:
            raise ValueError("score exceeds capacity")
        self.calls += 1
        return "handled by {}".format(self.name)


class ComplexityRouter:
    """Route each request to the cheapest sufficient expert."""

    def __init__(self) -> None:
        self.experts: list = []

    def add_expert(self, name: str, capacity: float, cost: float = 1.0) -> None:
        self.experts.append(Expert(name, capacity, cost))

    def route(self, vector: np.ndarray) -> Expert:
        if not self.experts:
            raise ValueError("no experts registered")
        score = complexity_score(vector)
        sufficient = [e for e in self.experts if e.capacity >= score]
        if not sufficient:
            raise ValueError("no expert can handle score {:.3f}".format(score))
        return min(sufficient, key=lambda e: (e.cost, e.capacity))

    def route_and_handle(self, vector: np.ndarray) -> str:
        expert = self.route(vector)
        return expert.handle(complexity_score(vector))

    def usage_report(self) -> dict:
        return {e.name: e.calls for e in self.experts}
