"""
markov_sc.py

Compatibility shim: MarkovSurrogateSC now just aliases the domain-agnostic
MarkovSurrogate (see markov.py). Kept so nothing that already imports
MarkovSurrogateSC breaks - use MarkovSurrogate directly for new code.
"""
from surrogate.markov import MarkovSurrogate


class MarkovSurrogateSC(MarkovSurrogate):
    """Compatibility shim. Use MarkovSurrogate directly."""

    def __init__(self, model_path, persona="aggregate", seed=42, smooth_epsilon=0.05):
        super().__init__(model_path, persona, seed, smooth_epsilon)
