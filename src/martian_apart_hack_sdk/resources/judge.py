from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:                     # avoids circular import at runtime
    from martian_apart_hack_sdk.backend import Backend

@dataclass
class Judge:
    """Local proxy for a *remote* Judge resource."""
    id: str
    llm: str
    rubrics: List[Dict[str, Any]]
    _backend: Backend = field(repr=False, compare=False)

    # ---------- Read helpers ----------------------------------

    def refresh(self) -> Judge:
        """Pull the latest server state and mutate in-place."""
        data = self._backend.judges.get(self.id).to_dict()
        self.__dict__.update(data)
        return self

    # Add a convenient dict view for (de)serialising
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