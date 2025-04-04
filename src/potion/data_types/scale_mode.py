from enum import Enum


class ScaleMode(Enum):
    NEAREST = 0  # Nearest pixel sampling
    LINEAR = 1   # Linear filtering
    BEST = 2     # Anisotropic filtering
