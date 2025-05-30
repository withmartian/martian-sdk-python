"""Judge API client functions."""

import dataclasses
import json
from typing import Any, Dict, List, Optional, Union

import httpx
from openai.types.chat import chat_completion

from martian_apart_hack_sdk import exceptions, judge_specs, utils
from martian_apart_hack_sdk.models.judge_evaluation import JudgeEvaluation
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
        judge_spec: Union[judge_specs.JudgeSpec, Dict[str, Any]],
        description: Optional[str] = None,
    ) -> judge_resource.Judge:
        """Create a judge.

        Args:
            judge_id (str): An arbitrary identifier (chosen by you) for the judge. You'll need to use this identifier to reference the judge in other API calls.
            judge_spec (Union[judge_specs.JudgeSpec, Dict[str, Any]]): The specification for the judge.
            description (Optional[str], optional): The description of the judge, for your own reference.

        Returns:
            judge_resource.Judge: The newly created judge resource.

        Raises:
            ResourceAlreadyExistsError: If a judge with the given ID already exists.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """

        if self._is_judge_exists(judge_id):
            raise exceptions.ResourceAlreadyExistsError(
                f"Judge with id {judge_id} already exists"
            )
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
            judge_resource.Judge: The new version of the judge.

            Judge updates are non-destructive. The updated judge will have an incremented version number.
            You can use this version number to reference the judge in other API calls.
            You can also access previous versions of the judge by passing the previous version number to the `get` method.

        Raises:
            ResourceNotFoundError: If the judge with the given ID does not exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        payload = self._get_judge_spec_payload(judge_spec.to_dict())
        # can't update labels/description in API
        resp = self.httpx.patch(f"/judges/{judge_id}", json=payload)
        resp.raise_for_status()
        return self._init_judge(json_data=resp.json())

    def list(self) -> list[judge_resource.Judge]:
        """List all judges in your organization.

        Returns:
            list[judge_resource.Judge]: A list of all judges.

        Raises:
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        resp = self.httpx.get("/judges")
        resp.raise_for_status()
        return [self._init_judge(j) for j in resp.json()["judges"]]

    def get(self, judge_id: str, version=None) -> judge_resource.Judge:
        """Get a specific judge by ID and optionally version.

        Args:
            judge_id (str): The ID of the judge to get.
            version (Optional[int], optional): The version of the judge to get. If not provided, the latest version will be returned.

        Returns:
            judge_resource.Judge: The judge resource. OR None if the judge does not exist.

        Raises:
            ResourceNotFoundError: If the judge with the given ID does not exist.
            httpx.HTTPError: If the request fails for reasons other than a missing judge.
            httpx.TimeoutException: If the request times out.
        """
        params = dict(version=version) if version else None
        resp = self.httpx.get(f"/judges/{judge_id}", params=params)

        if resp.status_code == 404:
            raise exceptions.ResourceNotFoundError(
                f"Judge with id {judge_id} does not exist"
            )

        resp.raise_for_status()
        return self._init_judge(resp.json())

    def get_versions(self, judge_id: str) -> List[judge_resource.Judge]:
        """Get all versions of a specific judge.

        Each time a judge is updated, a new version is created. This method returns all versions
        of a judge, ordered from newest to oldest.

        Args:
            judge_id (str): The ID of the judge to get versions for.

        Returns:
            List[judge_resource.Judge]: A list of all versions of the judge, ordered from newest to oldest.

        Raises:
            ResourceNotFoundError: If the judge with the given ID does not exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        resp = self.httpx.get(f"/judges/{judge_id}/versions")
        resp.raise_for_status()
        if not resp.json()["judges"]:
            raise exceptions.ResourceNotFoundError(
                f"Judge with id {judge_id} does not exist"
            )
        return [self._init_judge(j) for j in resp.json()["judges"]]

    def render_prompt(
        self,
        judge: judge_resource.Judge,
        completion_request: Dict[str, Any],
        completion_response: chat_completion.ChatCompletion,
    ) -> str:
        """Render the judging prompt for a judge.

        Concatenates the judge's prescript, rubric, and postscript;
        evaluates variables in the prompt (e.g. `${min_score}`, `${max_score}`, `${content}`);
        and returns the rendered prompt.

        This is useful for debugging or for getting a sense of what the judge will see,
        without having to run the judge or call the API.

        Args:
            judge (judge_resource.Judge): The judge to render the prompt for.
            completion_request (Dict[str, Any]): The completion request parameters that would be sent to the LLM.
            completion_response (chat_completion.ChatCompletion): The completion response from the LLM.

        Returns:
            str: The rendered prompt that would be sent to the Judge.

        Raises:
            ResourceNotFoundError: If the judge with the given ID does not exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out based on evaluation_timeout config.
        """
        payload = self._prepare_judge_evaluation_payload(
            judge, completion_request, completion_response
        )
        resp = self.httpx.post(
            f"/judges/{judge.id}:render",
            json=payload,
            timeout=self.config.evaluation_timeout,
        )
        resp.raise_for_status()
        return json.loads(resp.json()["prompt"])["rubric_judge"]

    def _prepare_judge_evaluation_payload(
        self, judge, completion_request, completion_response
    ):
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
        """Evaluate an LLM response using a specific judge.

        This method sends the completion request and response to the judge for evaluation.
        The judge will assess the response based on its rubric and return a structured evaluation.

        Args:
            judge (judge_resource.Judge): The judge to use for evaluation.
            completion_request (Dict[str, Any]): The original completion request parameters that were sent to the LLM.
            completion_response (chat_completion.ChatCompletion): The completion response from the LLM to evaluate.

        Returns:
            JudgeEvaluation: The evaluation results, including:
                - score: The numerical score assigned by the judge
                - reasoning: The judge's explanation for the score
                - metadata: Additional evaluation metadata

        Raises:
            ResourceNotFoundError: If the judge with the given ID does not exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out based on evaluation_timeout config.
        """
        payload = self._prepare_judge_evaluation_payload(
            judge, completion_request, completion_response
        )
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
        """Evaluate an LLM response using a judge specification directly.

        Similar to evaluate(), but instead of using a saved judge, this method accepts a judge
        specification directly. This is useful for testing new judge specifications before
        creating a permanent judge.

        Args:
            judge_spec (Dict[str, Any]): The judge specification to use for evaluation.
            completion_request (Dict[str, Any]): The original completion request parameters that were sent to the LLM.
            completion_response (chat_completion.ChatCompletion): The completion response from the LLM to evaluate.

        Returns:
            JudgeEvaluation: The evaluation results, including:
                - score: The numerical score assigned by the judge
                - reasoning: The judge's explanation for the score
                - metadata: Additional evaluation metadata

        Raises:
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out based on evaluation_timeout config.
        """
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
