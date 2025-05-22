"""Router API client functions."""

import dataclasses
from typing import Any, Dict, Optional

import httpx
from martian_apart_hack_sdk.exceptions import ResourceNotFoundError
from martian_apart_hack_sdk import utils
from martian_apart_hack_sdk.resources import router as router_resource


@dataclasses.dataclass(frozen=True)
class RoutersClient:
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
        if self._is_router_exists(router_id):
            raise ResourceNotFoundError(f"Router with id {router_id} already exists")
        router_spec = {
            'points': [
                {
                    'point': {
                        'x': 0.0,
                        'y': 0.0
                    },
                    'executor': {
                        'spec': {
                            'executor_type': 'ModelExecutor',
                            'model_name': base_model
                        }
                    }
                },
                {
                    'point': {
                        'x': 1.0,
                        'y': 1.0
                    },
                    'executor': {
                        'spec': {
                            'executor_type': 'ModelExecutor',
                            'model_name': base_model
                        }
                    }
                }
            ]
        }
        payload = self._get_router_spec_payload(router_spec)
        if description is not None:
            payload["description"] = description
        params = {"routerId": router_id}
        resp = self.httpx.post("/routers", params=params, json=payload)
        resp.raise_for_status()
        return self._init_router(json_data=resp.json())

    def list(self) -> list[router_resource.Router]:
        resp = self.httpx.get("/routers")
        return [self._init_router(j) for j in resp.json()["routers"]]

    def get(self, router_id: str, version=None) -> router_resource.Router:
        params = dict(version=version) if version else None
        resp = self.httpx.get(f"/routers/{router_id}", params=params)
        print(resp.json())
        resp.raise_for_status()
        return self._init_router(resp.json())
