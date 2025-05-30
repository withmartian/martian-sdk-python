"""Router API client functions."""

import dataclasses
import datetime as dt
import logging
import time
from typing import Any, Dict, List, Optional

import httpx
import openai
from openai.types.chat import chat_completion

from martian_apart_hack_sdk import exceptions, utils
from martian_apart_hack_sdk.models import router_constraints, router_training_job
from martian_apart_hack_sdk.resources import judge as judge_resource
from martian_apart_hack_sdk.resources import router as router_resource

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class RoutersClient:
    """The client for the Martian Routers API. Use the RoutersClient to create, update, and list routers.

    Normally, you don't need to create a RoutersClient directly. Instead, use the MartianClient.routers property to access the RoutersClient.

    Args:
        httpx (httpx.Client): The HTTP client to use for the API.
        config (utils.ClientConfig): The configuration for the API.
    """

    httpx: httpx.Client
    config: utils.ClientConfig

    def _init_router(self, json_data):
        return router_resource.Router(
            name=json_data["name"],
            version=json_data["version"],
            description=json_data["description"],
            createTime=json_data["createTime"],
            routerSpec=json_data.get("routerSpec"),
        )

    def _is_router_exists(self, router_id: str) -> bool:
        resp = self.httpx.get(f"/routers/{router_id}")
        return resp.status_code == 200

    @staticmethod
    def _get_router_spec_payload(router_spec: Dict[str, Any]) -> Dict[str, Any]:
        return {"routerSpec": router_spec}

    def create_router(
        self,
        router_id: str,
        base_model: str,
        description: Optional[str] = None,
    ) -> router_resource.Router:
        """Create a router.

        Args:
            router_id (str): An arbitrary identifier (chosen by you) for the router. You'll need to use this identifier to reference the router in other API calls.
            base_model (str): The base model to use for the router.
            description (Optional[str], optional): The description of the router, for your own reference.

        Returns:
            router_resource.Router: The newly created router resource.

        Raises:
            ResourceAlreadyExistsError: If a router with the given ID already exists.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        if self._is_router_exists(router_id):
            raise exceptions.ResourceAlreadyExistsError(
                f"Router with id {router_id} already exists"
            )
        router_spec = {
            "points": [
                self._get_model_executor(base_model, x=0.0, y=0.0),
                self._get_model_executor(base_model, x=1.0, y=1.0),
            ]
        }
        payload = self._get_router_spec_payload(router_spec)
        if description is not None:
            payload["description"] = description
        params = {"routerId": router_id}
        resp = self.httpx.post("/routers", params=params, json=payload)
        resp.raise_for_status()
        return self._init_router(json_data=resp.json())

    @staticmethod
    def _get_model_executor(base_model, x, y):
        return {
            "point": {"x": x, "y": y},
            "executor": {
                "spec": {"executor_type": "ModelExecutor", "model_name": base_model}
            },
        }

    def update_router(
        self,
        router_id: str,
        router_spec: Dict[str, Any],
        description: Optional[str] = None,
    ) -> router_resource.Router:
        """Update an existing router's specification and/or description.

        Args:
            router_id (str): The ID of the router to update.
            router_spec (Dict[str, Any]): The new router specification.
            description (Optional[str], optional): Optional new description for the router.

        Returns:
            router_resource.Router: The updated Router resource.

        Notes:
            Router updates are non-destructive. The updated router will have an incremented version number.
            You can use this version number to reference the router in other API calls.
            You can also access previous versions of the router by passing the previous version number to the `get` method.

        Raises:
            ResourceNotFoundError: If the router doesn't exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        if not self._is_router_exists(router_id):
            raise exceptions.ResourceNotFoundError(
                f"Router with id {router_id} not found"
            )

        payload = self._get_router_spec_payload(router_spec)
        if description is not None:
            payload["description"] = description

        resp = self.httpx.patch(f"/routers/{router_id}", json=payload)
        resp.raise_for_status()
        return self._init_router(json_data=resp.json())

    def list(self) -> list[router_resource.Router]:
        """List all routers.

        Returns:
            list[router_resource.Router]: A list of all available routers.

        Raises:
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        resp = self.httpx.get("/routers")
        resp.raise_for_status()
        return [self._init_router(j) for j in resp.json()["routers"]]

    def get(self, router_id: str, version=None) -> router_resource.Router:
        """Get a specific router by ID and optionally version.

        Args:
            router_id (str): The ID of the router to retrieve.
            version (Optional[int], optional): The specific version of the router to retrieve. If not provided, the latest version will be returned.

        Returns:
            router_resource.Router: The router resource. OR None if the router does not exist.

        Raises:
            ResourceNotFoundError: If the router doesn't exist.
            httpx.HTTPError: If the request fails for reasons other than a missing router.
            httpx.TimeoutException: If the request times out.
        """
        params = dict(version=version) if version else None
        resp = self.httpx.get(f"/routers/{router_id}", params=params)

        if resp.status_code == 404:
            raise exceptions.ResourceNotFoundError(
                f"Router with id {router_id} not found"
            )

        resp.raise_for_status()
        return self._init_router(resp.json())

    def run(
        self,
        router: router_resource.Router,
        routing_constraint: router_constraints.RoutingConstraint,
        completion_request: Dict[str, Any],
        version: Optional[int] = None,
    ) -> chat_completion.ChatCompletion:
        """Run a router with the given constraints and completion request.

        Args:
            router_id (str): The ID of the router to run.
            routing_constraint (RoutingConstraint): The routing constraints to apply.
            completion_request (Dict[str, Any]): The completion request parameters.
            version (Optional[int], optional): Optional router version to use.

        Returns:
            str: The router's response string.

        Raises:
            ResourceNotFoundError: If the router doesn't exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        if not self._is_router_exists(router.id):
            raise exceptions.ResourceNotFoundError(
                f"Router with id {router.id} not found"
            )

        openai_client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.openai_api_url,
        )

        extra_body = {
            **router_constraints.render_extra_body_router_constraint(routing_constraint)
        }
        if version is not None:
            version_to_use = version
        elif router.version is not None:
            version_to_use = router.version
        else:
            version_to_use = "latest"

        response = openai_client.chat.completions.create(
            **completion_request
            | {"model": f"{router.name}/versions/{version_to_use}"},
            extra_body=extra_body,
            timeout=self.config.evaluation_timeout,
        )
        return response

    def run_training_job(
        self,
        router: router_resource.Router,
        judge: judge_resource.Judge,
        llms: List[str],
        requests: List[Dict[str, Any]],
    ) -> router_training_job.RouterTrainingJob:
        """Train a router for a given set of models, using a judge and list of completion requests.

        Args:
            router (Router): The router to train.
            judge (Judge): The judge to use for evaluation.
            llms (List[str]): List of LLM model names to use.
            requests (List[Dict[str, Any]]): List of request objects containing messages for training.

        Returns:
            RouterTrainingJob: The training job response metadata.

            Note: The response metadata contains information about the training job itself,
            but does not contain any information about the results of training or router configuration.

        Raises:
            ResourceNotFoundError: If the router or judge doesn't exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.

        Examples:
            Create a simple judge and router, then train the router using example requests:

            >>> # Create a basic judge that evaluates response quality
            >>> judge_spec = RubricJudgeSpec(
            ...     model_type="rubric_judge",
            ...     model="gpt-4",
            ...     rubric="Rate the response quality from 1-10 based on accuracy and completeness.",
            ...     min_score=1,
            ...     max_score=10
            ... )
            >>> judge = client.judges.create("quality_judge", judge_spec)
            >>>
            >>> # Create a simple router
            >>> router = client.routers.create("test_router", RouterSpec(...))
            >>>
            >>> # Example training requests
            >>> requests = [
            ...     {
            ...         "messages": [
            ...             {"role": "user", "content": "What is Python?"}
            ...         ]
            ...     },
            ...     {
            ...         "messages": [
            ...             {"role": "system", "content": "You are a machine learning expert who explains concepts clearly and concisely."},
            ...             {"role": "user", "content": "Explain machine learning."}
            ...         ]
            ...     }
            ... ]
            >>>
            >>> # Train the router
            >>> training_job = client.routers.run_training_job(
            ...     router=router,
            ...     judge=judge,
            ...     llms=["gpt-4o-mini", "gpt-4.1-mini", "gpt-4o"],
            ...     requests=requests
            ... )
        """
        if llms is None or not llms:
            raise exceptions.InvalidParameterError(
                "At least one LLM model name must be provided"
            )
        if not isinstance(llms, list):
            raise exceptions.InvalidParameterError(
                "llms param must be a list of strings"
            )
        llm_models = list(set(llms))

        payload = {
            "routerName": router.name,
            "judgeName": judge.name,
            "llms": llm_models,
            "requests": requests,
        }

        resp = self.httpx.post("/router_training_jobs", json=payload)
        resp.raise_for_status()
        job = router_training_job.RouterTrainingJob.from_dict(resp.json())
        _LOGGER.info(
            "Started training job %s for router %s with judge %s and LLMs: %s",
            job.name,
            router.name,
            judge.name,
            llm_models,
        )
        return job

    def wait_training_job(
        self,
        job_name: str,
        poll_interval: int = 10,
        poll_timeout: int = 20 * 60,  # 20 minutes in seconds
    ) -> router_training_job.RouterTrainingJob:
        """Poll a training job until it completes or fails.

        Args:
            job_name (str): The job name or ID. If it contains '/' it's treated as a full name
                (e.g. 'organizations/org-name/router_training_jobs/job-id') and the last part is used as ID.
            poll_interval (int, optional): Number of seconds to wait between polls. Defaults to 10.
            poll_timeout (int, optional): Maximum time to poll in seconds. Defaults to 1200 (20 minutes).

        Returns:
            RouterTrainingJob: The final training job state. Check the `status` field to determine
                if the job completed successfully ("SUCCESS") or failed ("FAILURE", "FAILURE_WITHOUT_RETRY").

        Raises:
            httpx.HTTPError: If any API request fails.
            TimeoutError: If the job doesn't complete within the poll_timeout period.

        Examples:
            >>> # Start a training job
            >>> training_job = client.routers.run_training_job(...)
            >>>
            >>> # Poll until completion
            >>> final_job = client.routers.poll_training_job(
            ...     job_name=training_job.name,
            ...     poll_interval=15,    # Check every 15 seconds
            ...     poll_timeout=600     # Wait up to 10 minutes
            ... )
            >>>
            >>> if final_job.status == "SUCCESS":
            ...     print("Training completed successfully!")
            ... else:
            ...     print(f"Training failed with status: {final_job.status}")
        """
        # Extract job ID from full name if needed
        job_id = job_name.split("/")[-1] if "/" in job_name else job_name

        start_time = dt.datetime.now()
        timeout_time = start_time + dt.timedelta(seconds=poll_timeout)

        while True:
            current_time = dt.datetime.now()
            if current_time > timeout_time:
                raise TimeoutError(
                    f"Training job {job_id} did not complete within {poll_timeout} seconds"
                )

            job = self.poll_training_job(job_id)

            elapsed = current_time - start_time
            _LOGGER.info(
                "Training job %s status: %s (elapsed: %s)", job_id, job.status, elapsed
            )

            if job.status == "FAILURE_WITHOUT_RETRY":
                _LOGGER.info("Job failed. All attempts have been exhausted.")
                if job.error_message:
                    _LOGGER.error("Error message: %s", job.error_message)
                _LOGGER.info("Retry count: %d", job.retry_count)

            if job.status == "FAILURE":
                _LOGGER.info("Job failed.")
                if job.error_message:
                    _LOGGER.error("Error message: %s", job.error_message)
                _LOGGER.info("Retry count: %d", job.retry_count)

            if job.status in ["SUCCESS", "FAILURE_WITHOUT_RETRY", "FAILURE"]:
                _LOGGER.info(
                    "Training job %s completed with status: %s", job_id, job.status
                )
                return job

            time.sleep(poll_interval)

    def poll_training_job(
        self,
        job_name: str,
    ) -> router_training_job.RouterTrainingJob:
        """Get the current status of a training job.

        Args:
            job_name (str): The job name or ID. If it contains '/' it's treated as a full name
                (e.g. 'organizations/org-name/router_training_jobs/job-id') and the last part is used as ID.

        Returns:
            RouterTrainingJob: The current state of the training job. Check the `status` field to determine
                if the job is still running ("RUNNING"), completed successfully ("SUCCESS"),
                or failed ("FAILURE", "FAILURE_WITHOUT_RETRY").

        Raises:
            ResourceNotFoundError: If the training job doesn't exist.
            httpx.HTTPError: If the request fails.
            httpx.TimeoutException: If the request times out.
        """
        job_id = job_name.split("/")[-1] if "/" in job_name else job_name
        resp = self.httpx.get(f"/router_training_jobs/{job_id}")
        resp.raise_for_status()
        return router_training_job.RouterTrainingJob.from_dict(resp.json())
