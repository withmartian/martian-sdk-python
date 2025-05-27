"""Router API client functions."""

import dataclasses
import json
from typing import Any, Dict, Optional

import httpx
from martian_apart_hack_sdk.exceptions import ResourceNotFoundError
from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.resources import router as router_resource
from martian_apart_hack_sdk.models.RouterConstraints import RoutingConstraint
from martian_apart_hack_sdk.resources.router import Router


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
            ResourceNotFoundError: If a router with the given ID already exists.
        """
        if self._is_router_exists(router_id):
            raise ResourceNotFoundError(f"Router with id {router_id} already exists")
        router_spec = {
            'points': [
                self._get_model_executor(base_model, x=0.0, y=0.0),
                self._get_model_executor(base_model, x=1.0, y=1.0)
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
            'point': {
                'x': x,
                'y': y
            },
            'executor': {
                'spec': {
                    'executor_type': 'ModelExecutor',
                    'model_name': base_model
                }
            }
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
            raise ResourceNotFoundError(f"Router with id {router_id} not found")
            
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
            version (Optional[int], optional): The specific version of the router to retrieve.

        Returns:
            Optional[Router]: The requested router if found, None otherwise.
        """
        params = dict(version=version) if version else None
        resp = self.httpx.get(f"/routers/{router_id}", params=params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._init_router(resp.json())

    def run(
        self,
        router_id: str,
        routing_constraint: RoutingConstraint,
        completion_request: Dict[str, Any],
        version: Optional[int] = None,
    ) -> str:
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
        if not self._is_router_exists(router_id):
            raise ResourceNotFoundError(f"Router with id {router_id} not found")

        payload = {
            "router": router_id,
            "routingConstraint": routing_constraint.to_dict(),
            "completionCreateParams": utils.get_evaluation_json_payload(completion_request)
        }
        if version is not None:
            payload["routerVersion"] = version

        resp = self.httpx.post(
            f"/routers/{router_id}:run",
            json=payload,
            timeout=self.config.evaluation_timeout,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    
