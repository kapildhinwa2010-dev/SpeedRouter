# SpeedRouter - Route batches to the expert predicted to serve them fastest
# Part of the Kapildhinwa2010-dev Toolkit.

"""SpeedRouter - latency-based request routing.

Lineage: DNA_DYNIMO routers. Each expert declares a latency model
(fixed base cost plus per-item cost) and a maximum batch size. The
router predicts each expert latency for the request and picks the
fastest expert that can accept the batch, with declared cost as a
tie-break.

Latencies are declared estimates, not measurements: the router is only
as honest as the numbers it is given. See README limitations.
"""

from __future__ import annotations

__all__ = ["estimate_latency", "SpeedExpert", "SpeedRouter"]


def estimate_latency(base_ms: float, per_item_ms: float, n_items: int) -> float:
    """Predicted latency in ms: base plus per-item cost times batch size."""
    if base_ms < 0 or per_item_ms < 0:
        raise ValueError("latencies must be >= 0")
    if n_items <= 0:
        raise ValueError("n_items must be > 0")
    return float(base_ms) + float(per_item_ms) * n_items


class SpeedExpert:
    """A routing target with a latency model and a batch-size limit."""

    def __init__(self, name: str, base_ms: float, per_item_ms: float,
                 max_items: int, cost: float = 1.0) -> None:
        if not name:
            raise ValueError("name must be non-empty")
        if max_items <= 0:
            raise ValueError("max_items must be > 0")
        if cost < 0:
            raise ValueError("cost must be >= 0")
        self.name = name
        self.base_ms = float(base_ms)
        self.per_item_ms = float(per_item_ms)
        self.max_items = int(max_items)
        self.cost = float(cost)
        self.calls = 0
        self.predicted_ms_total = 0.0

    def can_accept(self, n_items: int) -> bool:
        return n_items <= self.max_items

    def handle(self, n_items: int) -> str:
        if not self.can_accept(n_items):
            raise ValueError("batch of {} exceeds max_items {}".format(n_items, self.max_items))
        ms = estimate_latency(self.base_ms, self.per_item_ms, n_items)
        self.predicted_ms_total += ms
        self.calls += 1
        return "served by {} ({:.1f} ms predicted)".format(self.name, ms)


class SpeedRouter:
    """Route each batch to the expert with the lowest predicted latency."""

    def __init__(self) -> None:
        self.experts: list = []

    def add_expert(self, name: str, base_ms: float, per_item_ms: float,
                   max_items: int, cost: float = 1.0) -> None:
        self.experts.append(SpeedExpert(name, base_ms, per_item_ms, max_items, cost))

    def route(self, n_items: int) -> SpeedExpert:
        if not self.experts:
            raise ValueError("no experts registered")
        if n_items <= 0:
            raise ValueError("n_items must be > 0")
        candidates = [e for e in self.experts if e.can_accept(n_items)]
        if not candidates:
            raise ValueError("no expert accepts a batch of {}".format(n_items))
        return min(candidates, key=lambda e: (estimate_latency(e.base_ms, e.per_item_ms, n_items), e.cost))

    def route_and_handle(self, n_items: int) -> str:
        return self.route(n_items).handle(n_items)

    def latency_report(self) -> dict:
        return {e.name: e.predicted_ms_total for e in self.experts}
