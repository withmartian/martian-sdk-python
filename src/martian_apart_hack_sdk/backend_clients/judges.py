"""Judge API client functions."""

import dataclasses
import json
from typing import Any, Dict, Optional, Union, List

import httpx
from openai.types.chat import chat_completion, chat_completion_message_param

from martian_apart_hack_sdk import judge_specs, utils
from martian_apart_hack_sdk.exceptions import ResourceNotFoundError
from martian_apart_hack_sdk.models.JudgeEvaluation import JudgeEvaluation
from martian_apart_hack_sdk.resources import judge as judge_resource


@dataclasses.dataclass(frozen=True)
class JudgesClient:
    """The client for the Martian Judges API. Use the JudgesClient to create, update, and list judges.

    Normally, you don't need to create a JudgesClient directly. Instead, use the MartianClient.judges property to access the JudgesClient.

    Args:
        httpx (httpx.Client): The HTTP client to use for the API.
        config (utils.ClientConfig): The configuration for the API.
    """
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
        judge_spec: Union[judge_specs.JudgeSpec,Dict[str, Any]],
        description: Optional[str] = None,
    ) -> judge_resource.Judge:
        """Create a judge.
        
        Args:
            judge_id (str): An arbitrary identifier (chosen by you) for the judge. You'll need to use this identifier to reference the judge in other API calls.
            judge_spec (Union[judge_specs.JudgeSpec, Dict[str, Any]]): The specification for the judge.
            description (Optional[str], optional): The description of the judge, for your own reference.
        """

        if self._is_judge_exists(judge_id):
            raise ResourceNotFoundError(f"Judge with id {judge_id} already exists")
        if not isinstance(judge_spec, dict):
            judge_spec = judge_spec.to_dict()
        payload = self._get_judge_spec_payload(judge_spec)
        if description is not None:
            payload["description"] = description
        params = {"judgeId": judge_id}
        resp = self.httpx.post("/judges", params=params, json=payload)
        resp.raise_for_status()
        return self._init_judge(json_data=resp.json())

    def update_judge(
        self, judge_id: str, judge_spec: judge_specs.JudgeSpec
    ) -> judge_resource.Judge:
        """Update a judge.
        
        Args:
            judge_id (str): The ID of the judge to update.
            judge_spec (judge_specs.JudgeSpec): The new specification for the judge.

        Returns:
            The new version of the judge.

            Note: Judge updates are non-destructive. The updated judge will have an incremented version number. You can use this version number to reference the judge in other API calls.
            You can also access previous versions of the judge by passing the previous verison number to the `get` method.
        """
        payload = self._get_judge_spec_payload(judge_spec.to_dict())
        # can't update labels/description in API
        resp = self.httpx.patch(f"/judges/{judge_id}", json=payload)
        resp.raise_for_status()
        return self._init_judge(json_data=resp.json())

    def list(self) -> list[judge_resource.Judge]:
        """List all judges.
        
        Returns:
            A list of all judges.
        """
        resp = self.httpx.get("/judges")
        resp.raise_for_status()
        return [self._init_judge(j) for j in resp.json()["judges"]]

    def get(self, judge_id: str, version=None) -> Optional[judge_resource.Judge]:
        """Get a judge.
        
        Args:
            judge_id (str): The ID of the judge to get.
            version (Optional[int], optional): The version of the judge to get.
        """
        params = dict(version=version) if version else None
        resp = self.httpx.get(f"/judges/{judge_id}", params=params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._init_judge(resp.json())

    def get_versions(self, judge_id: str) -> List[judge_resource.Judge]:
        resp = self.httpx.get(f"/judges/{judge_id}/versions")
        resp.raise_for_status()
        if not resp.json()["judges"]:
            raise ResourceNotFoundError(f"Judge with id {judge_id} does not exist")
        return [self._init_judge(j) for j in resp.json()["judges"]]

    def render_prompt(self, judge: judge_resource.Judge,
        completion_request: Dict[str, Any],
        completion_response: chat_completion.ChatCompletion,
    ) -> str:
        """
        This method render judging prompt. It works only for rubric judge
        :param judge:
        :param completion_request:
        :param completion_response:
        :return: str: rendered prompt
        """
        payload = self._prepare_judge_evaluation_payload(judge, completion_request, completion_response)
        resp = self.httpx.post(
            f"/judges/{judge.id}:render",
            json=payload,
            timeout=self.config.evaluation_timeout,
        )
        resp.raise_for_status()
        return json.loads(resp.json()["prompt"])["rubric_judge"]


    def _prepare_judge_evaluation_payload(self, judge, completion_request, completion_response):
        request_payload = utils.get_evaluation_json_payload(completion_request)
        completion_payload = utils.get_evaluation_json_payload(
            # Cost and response fields are required by evaluate judge API
            self._ensure_cost_response_in_completion(completion_response)
        )
        payload = {
            "judgeVersion": judge.version,
            "completionCreateParams": request_payload,
            "chatCompletion": completion_payload,
        }
        return payload

    @staticmethod
    def _get_evaluation_json_payload(data: Dict[str, Any]):
        return {"jsonPayload": json.dumps(data)}

    @staticmethod
    def _ensure_cost_response_in_completion(completion: chat_completion.ChatCompletion):
        return {
            "cost": 0.0,
            "response": completion.choices[0].message.to_dict(),
        } | completion.to_dict()

    def evaluate(
        self,
        judge: judge_resource.Judge,
        completion_request: Dict[str, Any],
        completion_response: chat_completion.ChatCompletion,
    ) -> JudgeEvaluation:
        payload = self._prepare_judge_evaluation_payload(judge, completion_request, completion_response)
        resp = self.httpx.post(
            f"/judges/{judge.id}:evaluate",
            json=payload,
            timeout=self.config.evaluation_timeout,
        )
        resp.raise_for_status()
        return JudgeEvaluation(**resp.json()["judgement"])

    def evaluate_using_judge_spec(
        self,
        judge_spec: Dict[str, Any],
        completion_request: Dict[str, Any],
        completion_response: chat_completion.ChatCompletion,
    ) -> JudgeEvaluation:
        request_payload = utils.get_evaluation_json_payload(completion_request)
        completion_payload = utils.get_evaluation_json_payload(
            self._ensure_cost_response_in_completion(completion_response)
        )
        payload = self._get_judge_spec_payload(judge_spec) | {
            "completionCreateParams": request_payload,
            "chatCompletion": completion_payload,
        }
        resp = self.httpx.post(
            "/judges:evaluate", json=payload, timeout=self.config.evaluation_timeout
        )
        resp.raise_for_status()
        return JudgeEvaluation(**resp.json()["judgement"])
