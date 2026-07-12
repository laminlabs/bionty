import warnings

warnings.warn(
    "`bionty.ids` is deprecated, use `bionty.uids` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from .uids import *  # noqa: F403
