from typing import Callable, Dict, Any

def _load_random_policy():
    from haic_env_builder.adapters.random_policy import RandomDiscretePolicy
    return RandomDiscretePolicy

RUNTIME_POLICIES: Dict[str, Callable[[], Any]] = {
    "random_discrete": _load_random_policy,
}

def make_policy(name: str, **kw):
    factory = RUNTIME_POLICIES.get(name)
    if not factory:
        raise KeyError(f"Unknown policy: {name}")
    cls = factory()
    return cls(**kw)
