from __future__ import annotations
from dataclasses import dataclass, field, InitVar
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:                     # avoids circular import at runtime
    from martian_apart_hack_sdk.backend import Backend

@dataclass(frozen=True, repr=True, eq=True, order=True)
class Judge:
    """Local proxy for a *remote* Judge resource."""
    id: str = field(init=False)
    version: int
    description: str
    createTime: str
    name: str
    judgeSpec: Dict[str, Any]

    _backend: Backend = field(repr=False, compare=False)

    def __post_init__(self):
        # Set id as the last segment after the last "/"
        _id = self.name.rsplit("/", 1)[-1]
        object.__setattr__(self, "id", _id)

    def refresh(self) -> Judge:
        """Pull the latest server state and mutate in-place."""
        return self._backend.judges.get(self.id)


    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    # ---------- Evaluate -------------------------------------

    def evaluate(self, prompt: str, output: str) -> Dict[str, Any]:
        """
        Remote call:
        POST /judges/{id}/evaluate  →  {overall: float, by_rubric: {...}}
        """
        return self._backend.judges.evaluate(self.id, prompt, output)

    def passes(self, prompt: str, output: str, *, threshold: float = 0.8) -> bool:
        return self.evaluate(prompt, output)["overall"] >= threshold

    # ---------- CRUD shortcuts -------------------------------

    def update(self, **fields) -> "Judge":
        """PATCH the Judge on the server, then mutate this proxy."""
        data = self._backend.judges.update(self.id, **fields).to_dict()
        self.__dict__.update(data)
        return self

    def delete(self) -> None:
        """DELETE /judges/{id}"""
        self._backend.judges.delete(self.id)