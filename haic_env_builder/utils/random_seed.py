# haic_env_builder/utils/random_seed.py
from __future__ import annotations
import os
import random
from typing import Optional

def set_all_seeds(seed: int, *, deterministic_torch: bool = True) -> None:
    """
    Set seeds for Python, NumPy, Torch (if installed), JAX (if installed),
    and make hashing & cuDNN behavior deterministic where possible.
    Safe to call even if optional libs are missing.
    """
    # 1) Python & hashing
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import hashlib
        # ensure repeatable hash-based ops if any
        hashlib.md5(b"seed")  # noop just to touch module
    except Exception:
        pass

    # 2) Python RNG
    random.seed(seed)

    # 3) NumPy
    try:
        import numpy as np
        try:
            # new Generator API (NumPy >= 1.17)
            np.random.seed(seed)  # still affects legacy RandomState users
            # If you use Generator elsewhere, create it like:
            # rng = np.random.default_rng(seed)
        except Exception:
            np.random.seed(seed)
    except Exception:
        pass

    # 4) PyTorch (optional)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        if deterministic_torch:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            # new flag (PyTorch 2.x) — safe to guard
            try:
                torch.use_deterministic_algorithms(True)
            except Exception:
                pass
    except Exception:
        pass

    # 5) JAX (optional)
    try:
        import jax
        import jax.random as jrandom
        # store a key globally if you want; for now just touch
        _ = jrandom.PRNGKey(seed)
        # enforce determinism where possible
        os.environ.setdefault("JAX_ENABLE_X64", "true")
    except Exception:
        pass

__all__ = ["set_all_seeds"]
