from typing import Optional
import os
import random

def set_global_seed(seed: Optional[int]):
    """
    Set seeds for random, numpy, and torch (if present). If seed is None,
    do nothing and allow non-deterministic behavior.
    """
    if seed is None:
        return

    random.seed(seed)

    try:
        import numpy as np  # type: ignore
        np.random.seed(seed)
    except Exception:
        pass

    try:
        import torch  # type: ignore
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        # For stricter determinism on PyTorch (optional, can slow things down)
        torch.backends.cudnn.deterministic = True  # type: ignore[attr-defined]
        torch.backends.cudnn.benchmark = False     # type: ignore[attr-defined]
    except Exception:
        pass

    # Some libs read PYTHONHASHSEED for hashing determinism
    os.environ["PYTHONHASHSEED"] = str(seed)