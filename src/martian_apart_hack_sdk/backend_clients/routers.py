"""Router API client functions."""

import dataclasses
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import openai
from openai.resources.chat.completions import completions

from martian_apart_hack_sdk import exceptions, utils
from martian_apart_hack_sdk.models.RouterConstraints import (
    RoutingConstraint,
    render_extra_body_router_constraint,
)
from martian_apart_hack_sdk.models.RouterTrainingJob import RouterTrainingJob
from martian_apart_hack_sdk.resources import router as router_resource
from martian_apart_hack_sdk.resources.judge import Judge
from martian_apart_hack_sdk.resources.router import Router

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
        """
        resp = self.httpx.get("/routers")
        resp.raise_for_status()
        return [self._init_router(j) for j in resp.json()["routers"]]

    def get(self, router_id: str, version=None) -> Optional[Router]:
        """Get a specific router by ID and optionally version.

        Args:
            router_id (str): The ID of the router to retrieve.
            version (Optional[int], optional): The specific version of the router to retrieve. If not provided, the latest version will be returned.

        Returns:
            router_resource.Router: The router resource. OR None if the router does not exist.
        """
        params = dict(version=version) if version else None
        resp = self.httpx.get(f"/routers/{router_id}", params=params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._init_router(resp.json())

    def run(
        self,
        router: Router,
        routing_constraint: RoutingConstraint,
        completion_request: Dict[str, Any],
        version: Optional[int] = None,
    ) -> completions.ChatCompletion:
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
        """
        if not self._is_router_exists(router.id):
            raise exceptions.ResourceNotFoundError(
                f"Router with id {router.id} not found"
            )

        openai_client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.openai_api_url,
        )

        extra_body = {**render_extra_body_router_constraint(routing_constraint)}
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
        router: Router,
        judge: Judge,
        llms: List[str],
        requests: List[Dict[str, Any]],
    ) -> RouterTrainingJob:
        """Run a training job for a router with the specified parameters.

        Args:
            router: The router to train
            judge: The judge to use for evaluation
            llms: List of LLM model names to use
            requests: List of request objects containing messages for training

        Returns:
            The training job response data

        Raises:
            httpx.HTTPError: If the request fails
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
        job = RouterTrainingJob.from_dict(resp.json())
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
    ) -> RouterTrainingJob:
        """Poll a training job until it completes or fails.

        Args:
            job_name: The job name or ID. If it contains '/' it's treated as a full name and the last part is used as ID
            poll_interval: Number of seconds to wait between polls (default: 10)
            poll_timeout: Maximum time to poll in seconds (default: 20 minutes)

        Returns:
            The final RouterTrainingJob instance

        Raises:
            httpx.HTTPError: If the request fails
            TimeoutError: If the job doesn't complete within the timeout period
        """
        # Extract job ID from full name if needed
        job_id = job_name.split("/")[-1] if "/" in job_name else job_name

        start_time = datetime.now()
        timeout_time = start_time + timedelta(seconds=poll_timeout)

        while True:
            current_time = datetime.now()
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
    ) -> RouterTrainingJob:
        """Poll status of a training job.

        Args:
            job_name: The job name or ID. If it contains '/' it's treated as a full name and the last part is used as ID

        Returns:
            The final RouterTrainingJob instance
        """
        job_id = job_name.split("/")[-1] if "/" in job_name else job_name
        resp = self.httpx.get(f"/router_training_jobs/{job_id}")
        resp.raise_for_status()
        return RouterTrainingJob.from_dict(resp.json())
