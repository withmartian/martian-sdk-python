from __future__ import annotations

import dataclasses
from typing import Any, Dict


@dataclasses.dataclass(frozen=True, repr=True, eq=True, order=True)
class Router:
    """Local proxy for a *remote* Router resource."""

    id: str = dataclasses.field(init=False)
    version: int
    description: str
    createTime: str
    name: str
    routerSpec: Dict[str, Any]

    def __post_init__(self):
        # Set id as the last segment after the last "/"
        _id = self.name.rsplit("/", 1)[-1]
        object.__setattr__(self, "id", _id) 