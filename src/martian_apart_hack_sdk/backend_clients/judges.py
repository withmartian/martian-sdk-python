"""Judge API client functions."""

import dataclasses
from typing import Any, Dict, Optional

import httpx
from openai.types.chat import chat_completion, chat_completion_message_param

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.resources import judge as judge_resource


@dataclasses.dataclass(frozen=True)
class JudgesClient:
    httpx: httpx.Client
    config: utils.ClientConfig

    def _init_judge(self, json_data):
        return judge_resource.Judge(
            name=json_data["name"],
            version=json_data["version"],
            description=json_data["description"],
            createTime=json_data["createTime"],
            judgeSpec=json_data.get("judgeSpec"),
        )

    def create_judge(
        self,
        judge_id: str,
        judge_spec: Dict[str, Any],
        description: Optional[str] = None,
    ) -> judge_resource.Judge:
        # TODO check that judge with judge_id is not exists before creating one (otherwise unclear 500 is returned
        # Another idea is to implement upsert_judge() method and/or get_or_create_judge() method

        payload: Dict[str, Any] = {"judgeSpec": {"judgeSpec": judge_spec}}
        if description is not None:
            payload["description"] = description
        print(payload)
        params = {"judgeId": judge_id}
        resp = self.httpx.post("/judges", params=params, json=payload)
        resp.raise_for_status()
        return self._init_judge(json_data=resp.json())

    def list(self) -> list[judge_resource.Judge]:
        resp = self.httpx.get("/judges")
        return [self._init_judge(j) for j in resp.json()["judges"]]

    def get(self, judge_id: str, version=None) -> judge_resource.Judge:
        params = dict(version=version) if version else None
        resp = self.httpx.get(f"/judges/{judge_id}", params=params)
        resp.raise_for_status()
        print(resp.json())
        return self._init_judge(resp.json())

    # TODO: Response type.
    def evaluate_judge(
        self,
        judge: judge_resource.Judge,
        completion_request: chat_completion_message_param.ChatCompletionMessageParam,
        completion: chat_completion.ChatCompletion,
    ) -> None:
        params = {
            "judge": judge.id,
            "judgeVersion": judge.version,
            "completionCreateParams": completion_request,
            "chatCompletion": completion,
            # TODO: Work out why router is required.
            "router": "",
        }
        resp = self.httpx.post("/judges:evaluate", params=params)
        resp.raise_for_status()
        print(resp.json())

    # TODO: Response type.
    def evaluate_judge_spec(
        self,
        judge_spec,
        completion_request: chat_completion_message_param.ChatCompletionMessageParam,
        completion: chat_completion.ChatCompletion,
    ) -> None:
        body = {
            "judgeSpec": judge_spec.to_dict(),
            "completionCreateParams": completion_request,
            "chatCompletion": completion.model_dump_json(),
        }
        resp = self.httpx.post("/judges:evaluate", json=body)
        resp.raise_for_status()
        print(resp.json())

    # # U  (full or PATCH-style partial)
    # def update(self, judge_id: str, **fields) -> "Judge":
    #     resp = self._client.patch(f"/judges/{judge_id}", json=fields).json()
    #     return Judge(**resp, _http=self._client)
    #
    # # D
    # def delete(self, judge_id: str) -> None:
    #     self._client.delete(f"/judges/{judge_id}")
