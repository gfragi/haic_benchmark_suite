import pytest

@pytest.fixture
def sample_decisions():
    # Sorted by t; includes human+ai actions, durations/latencies, probs, surrogate,
    # off-role, progress, and an explicit error event to exercise all metrics.
    return [
        {"t": 0.0, "agent": "human1", "actor_type": "human",
         "action": "look", "duration_s": 0.8, "correct": True,
         "probs": {"look": 0.7, "skip": 0.3},
         "surrogate_probs": {"look": 0.6, "skip": 0.4}},
        {"t": 0.9, "event_type": "progress"},

        {"t": 1.0, "agent": "ai1", "actor_type": "ai",
         "action": "suggest", "latency_ms": 200, "correct": True,
         "probs": {"suggest": 0.9, "hold": 0.1},
         "surrogate_probs": {"suggest": 0.85, "hold": 0.15}},

        {"t": 1.2, "agent": "human1", "actor_type": "human",
         "action": "confirm", "duration_s": 0.6, "correct": True,
         "off_role_action": False, "probs": {"confirm": 0.8, "reject": 0.2},
         "surrogate_action": "confirm"},

        {"t": 2.0, "agent": "human1", "actor_type": "human",
         "action": "apply", "duration_s": 1.2, "correct": False,
         "off_role_action": True, "probs": {"apply": 0.4, "undo": 0.6},
         "surrogate_action": "undo"},

        {"t": 2.2, "event_type": "error"},

        {"t": 3.0, "agent": "human1", "actor_type": "human",
         "action": "finish", "duration_s": 0.7, "correct": True,
         "probs": {"finish": 0.9}},
    ]
