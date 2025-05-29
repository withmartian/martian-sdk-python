"""Resource models for Martian judges."""

from __future__ import annotations

import dataclasses
from typing import Any, Dict

from openai.types.chat import chat_completion, chat_completion_message_param


@dataclasses.dataclass(frozen=True, repr=True, eq=True, order=True)
class Judge:
    """A Judge resource representing a Martian judge configuration.

    This class serves as the primary interface for judge operations in the SDK.
    Judge instances are returned by JudgeClient methods (`create_judge`, `get`, `list`)
    and are used as parameters for operations like evaluating completions or training routers.

    Judges should not be created from this class. Instead, use the `JudgeClient` to create and manage judges.

    The Judge is immutable. You can not update it directly from instances of this class.
    Instead, use the `JudgeClient` to update the judge.
    Any updates create a new version of the judge with an incremented version number.
    Previous versions remain accessible through the `JudgeClient.get()` method.

    Attributes:
        id (str): The judge's identifier.
        version (int): The judge version number. Increments with each update.
        description (str): A human-readable description of the judge's purpose.
        createTime (str): When the judge was created (RFC 3339 format).
        name (str): The judge's full resource name (format: "organizations/{org}/judges/{judge_id}").
        judgeSpec (Dict[str, Any]): The judge's configuration, including rubric and evaluation settings.
    """

    id: str = dataclasses.field(init=False)
    version: int
    description: str
    createTime: str
    name: str
    judgeSpec: Dict[str, Any]

    def __post_init__(self):
        """Extract the judge ID from the full resource name and set the `id` field.
        
        The ID is taken from the last segment of the name path. For example, from
        "organizations/org-123/judges/my-judge", the ID would be "my-judge".
        """
        # Set id as the last segment after the last "/"
        _id = self.name.rsplit("/", 1)[-1]
        object.__setattr__(self, "id", _id)

    # def refresh(self) -> Judge:
    #     """Pull the latest server state and mutate in-place."""
    #     return self._backend.judges.get(self.id)

    # def to_dict(self) -> Dict[str, Any]:
    #     return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

    # # ---------- Evaluate -------------------------------------

    # # TODO: Return type.
    # def evaluate(
    #     self,
    #     completion_request: chat_completion_message_param.ChatCompletionMessageParam,
    #     completion: chat_completion.ChatCompletion,
    # ) -> None:
    #     """
    #     Remote call:
    #     POST /judges/{id}/evaluate  →  {overall: float, by_rubric: {...}}
    #     """
    #     # TODO: Work out in which cases we want to evaluate a versioned judge,
    #     # and when we want to evaluate the judge spec only.
    #     return self._backend.judges.evaluate_judge(
    #         judge_id=self.id,
    #         judge_version=self.version,
    #         completion_request=completion_request,
    #         completion=completion,
    #     )

    # def passes(self, prompt: str, output: str, *, threshold: float = 0.8) -> bool:
    #     return self.evaluate(prompt, output)["overall"] >= threshold

    # # ---------- CRUD shortcuts -------------------------------

    # def update(self, **fields) -> "Judge":
    #     """PATCH the Judge on the server, then return new version"""
    #     data = self._backend.judges.update(self.id, **fields).to_dict()
    #     self.__dict__.update(data)
    #     return self

    # def delete(self) -> None:
    #     """DELETE /judges/{id}"""
    #     self._backend.judges.delete(self.id)
