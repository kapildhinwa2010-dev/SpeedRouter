import numpy as np
import pytest

from speedrouter import ComplexityRouter, Expert, complexity_score


def test_score_zero_vector():
    assert complexity_score(np.zeros(4)) == 0.0


def test_score_positive_for_signal():
    assert complexity_score(np.array([1.0, -1.0, 2.0])) > 0.0


def test_score_rejects_empty():
    with pytest.raises(ValueError):
        complexity_score(np.array([]))


def test_uniform_vector_lower_entropy_than_peaked():
    uniform = np.ones(16)
    peaked = np.zeros(16)
    peaked[0] = 5.0
    assert complexity_score(peaked) < complexity_score(uniform)


def test_expert_rejects_bad_params():
    with pytest.raises(ValueError):
        Expert("", 1.0)
    with pytest.raises(ValueError):
        Expert("e", 0.0)
    with pytest.raises(ValueError):
        Expert("e", 1.0, cost=-1.0)


def test_expert_counts_calls():
    expert = Expert("e", 10.0)
    expert.handle(1.0)
    expert.handle(2.0)
    assert expert.calls == 2


def test_expert_rejects_overflow():
    expert = Expert("e", 1.0)
    with pytest.raises(ValueError):
        expert.handle(5.0)


def test_router_prefers_cheapest_sufficient():
    router = ComplexityRouter()
    router.add_expert("tiny", capacity=1.0, cost=0.1)
    router.add_expert("big", capacity=100.0, cost=10.0)
    expert = router.route(np.full(4, 0.1))
    assert expert.name == "tiny"


def test_router_escapes_to_big_expert():
    router = ComplexityRouter()
    router.add_expert("tiny", capacity=0.5, cost=0.1)
    router.add_expert("big", capacity=100.0, cost=10.0)
    expert = router.route(np.full(8, 10.0))
    assert expert.name == "big"


def test_router_no_expert_raises():
    router = ComplexityRouter()
    router.add_expert("tiny", capacity=0.1, cost=0.1)
    with pytest.raises(ValueError):
        router.route(np.full(8, 100.0))


def test_router_empty_raises():
    router = ComplexityRouter()
    with pytest.raises(ValueError):
        router.route(np.ones(3))


def test_route_and_handle_and_report():
    router = ComplexityRouter()
    router.add_expert("tiny", capacity=10.0, cost=0.1)
    router.add_expert("big", capacity=100.0, cost=10.0)
    result = router.route_and_handle(np.ones(4))
    assert result == "handled by tiny"
    assert router.usage_report() == {"tiny": 1, "big": 0}
