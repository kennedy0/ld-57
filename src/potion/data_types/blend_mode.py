from enum import Enum


class BlendMode(Enum):
    NONE  = 0            # No blending        # noqa
    BLEND = 1            # Alpha blending     # noqa
    ADD   = 2            # Additive blending  # noqa
    MOD   = 3            # Color modulate     # noqa
    MUL   = 4            # Color multiply     # noqa
    ALPHA_COMPOSITE = 5  # Alpha composite    # noqa
