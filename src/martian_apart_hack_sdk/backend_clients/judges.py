"""Judge API client functions."""

import dataclasses
import json
from typing import Any, Dict, Optional

import httpx
from martian_apart_hack_sdk.exceptions import ResourceNotFoundError
from openai.types.chat import chat_completion, chat_completion_message_param

from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.judge_specs import JudgeSpec
from martian_apart_hack_sdk.models.JudgeEvaluation import JudgeEvaluation
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
            judgeSpec=json_data.get("judgeSpec", {}).get("judgeSpec"),
        )

    def _is_judge_exists(self, judge_id: str) -> bool:
        resp = self.httpx.get(f"/judges/{judge_id}")
        return resp.status_code == 200

    @staticmethod
    def _get_judge_spec_payload(judge_spec: Dict[str, Any]) -> Dict[str, Any]:
        return {"judgeSpec": {"judgeSpec": judge_spec}}

    def create_judge(
            self,
            judge_id: str,
            judge_spec: Dict[str, Any],
            description: Optional[str] = None,
    ) -> judge_resource.Judge:
        if self._is_judge_exists(judge_id):
            raise ResourceNotFoundError(f"Judge with id {judge_id} already exists")
        payload = self._get_judge_spec_payload(judge_spec)
        if description is not None:
            payload["description"] = description
        params = {"judgeId": judge_id}
        resp = self.httpx.post("/judges", params=params, json=payload)
        resp.raise_for_status()
        return self._init_judge(json_data=resp.json())

    def update_judge(self, judge_id: str, judge_spec: Dict[str, Any]) -> judge_resource.Judge:
        payload = self._get_judge_spec_payload(judge_spec)
        print(payload)
        # can't update labels/description in API
        resp = self.httpx.patch(f"/judges/{judge_id}", json=payload)
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

    @staticmethod
    def _get_evaluation_json_payload(data: Dict[str, Any]):
        return {"jsonPayload": json.dumps(data)}

    @staticmethod
    def _ensure_cost_response_in_completion(completion: chat_completion.ChatCompletion):
        return {
            "cost": 0.0,
            "response": completion.choices[0].message.to_dict(),
        } | completion.to_dict()

    def evaluate_judge(
            self,
            judge: judge_resource.Judge,
            completion_request: Dict[str, Any],
            completion_response: chat_completion.ChatCompletion,
    ) -> JudgeEvaluation:
        request_payload = self._get_evaluation_json_payload(completion_request)
        completion_payload = self._get_evaluation_json_payload(
            # Cost and response fields are required by evaluate judge API 
            self._ensure_cost_response_in_completion(completion_response)
        )
        payload = {
            "judgeVersion": judge.version,
            "completionCreateParams": request_payload,
            "chatCompletion": completion_payload,
        }
        resp = self.httpx.post(f"/judges/{judge.id}:evaluate", json=payload, timeout=self.config.evaluation_timeout)
        resp.raise_for_status()
        return JudgeEvaluation(**resp.json()["judgement"])

    def evaluate_judge_spec(
        self,
        judge_spec: Dict[str, Any],
        completion_request: Dict[str, Any],
        completion_response: chat_completion.ChatCompletion,
    ) -> JudgeEvaluation:
        request_payload = self._get_evaluation_json_payload(completion_request)
        completion_payload = self._get_evaluation_json_payload(
            self._ensure_cost_response_in_completion(completion_response)
        )
        payload = self._get_judge_spec_payload(judge_spec) | {
            "completionCreateParams": request_payload,
            "chatCompletion": completion_payload,
        }
        resp = self.httpx.post("/judges:evaluate", json=payload, timeout=self.config.evaluation_timeout)
        resp.raise_for_status()
        return JudgeEvaluation(**resp.json()["judgement"])

    # U  (full or PATCH-style partial)
    def update(self, judge_id: str, **fields) -> "Judge":
        resp = self._client.patch(f"/judges/{judge_id}", json=fields).json()
        return Judge(**resp, _http=self._client)

    # D
    def delete(self, judge_id: str) -> None:
        self._client.delete(f"/judges/{judge_id}")
