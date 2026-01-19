# For Pylance/Pyright: allow kwargs in model constructors without per-class __init__.
from typing import TYPE_CHECKING, Any


class _ModelInitMixin:
    if TYPE_CHECKING:
        def __init__(self, **kwargs: Any) -> None: ...