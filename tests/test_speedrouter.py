"""Tests for SpeedRouter: latency-based batch routing."""

import pytest

from speedrouter import SpeedRouter, SpeedExpert, estimate_latency


def test_estimate_latency_linear():
    assert estimate_latency(10.0, 2.0, 5) == 20.0
    with pytest.raises(ValueError):
        estimate_latency(-1.0, 1.0, 1)
    with pytest.raises(ValueError):
        estimate_latency(1.0, 1.0, 0)


def test_expert_rejects_oversized_batch():
    expert = SpeedExpert("small", 5.0, 1.0, max_items=10)
    assert expert.can_accept(10)
    assert not expert.can_accept(11)
    with pytest.raises(ValueError):
        expert.handle(11)


def test_route_picks_fastest_for_small_batches():
    router = SpeedRouter()
    router.add_expert("slow-start", 50.0, 0.1, max_items=1000)
    router.add_expert("fast-start", 1.0, 5.0, max_items=1000)
    assert router.route(1).name == "fast-start"


def test_route_picks_per_item_expert_for_large_batches():
    router = SpeedRouter()
    router.add_expert("slow-start", 50.0, 0.1, max_items=1000)
    router.add_expert("fast-start", 1.0, 5.0, max_items=1000)
    assert router.route(100).name == "slow-start"


def test_route_respects_batch_limits():
    router = SpeedRouter()
    router.add_expert("small", 1.0, 1.0, max_items=10)
    router.add_expert("big", 100.0, 1.0, max_items=1000)
    assert router.route(50).name == "big"
    with pytest.raises(ValueError):
        router.route(5000)


def test_route_empty_router_raises():
    with pytest.raises(ValueError):
        SpeedRouter().route(1)


def test_route_and_handle_and_report():
    router = SpeedRouter()
    router.add_expert("e", 1.0, 1.0, max_items=10)
    out = router.route_and_handle(4)
    assert "served by e" in out
    assert router.latency_report()["e"] == pytest.approx(5.0)
