"""Resource models for Martian routers."""

from __future__ import annotations

import dataclasses
from typing import Any, Dict


@dataclasses.dataclass(frozen=True, repr=True, eq=True, order=True)
class Router:
    """A Router resource representing a Martian router configuration.

    This class serves as the primary interface for router operations in the SDK.
    Router instances are returned by RouterClient methods (`create_router`, `get`, `list`)
    and are used as parameters for operations like running the router or creating training jobs.

    Router Lifecycle:

    #. When first created, a router only routes to its base_model.
    #. To enable routing between multiple models, the router must be trained using run_training_job.
    #. After training, the router can intelligently route between any of the models it was trained on,
       based on quality vs latency preferences specified in routing constraints.

    Routers should not be created from this class. Instead, use the `RouterClient` to create and manage routers.

    The Router is immutable. You can not update it directly from instances of this class.
    Instead, use the `RouterClient` to update the router.
    Any updates create a new version of the router with an incremented version number.
    Previous versions remain accessible through the `RouterClient.get()` method.

    Attributes:
        id (str): The router's identifier.
        version (int): The router version number. Increments with each update.
        description (str): A human-readable description of the router's purpose.
        createTime (str): When the router was created (RFC 3339 format).
        name (str): The router's full resource name (format: "organizations/{org}/routers/{router_id}").
        routerSpec (Dict[str, Any]): The router's configuration, including points and executors.
            After training, this includes configuration for routing between all models the router was trained on.

    Note:
        While this class has public attributes, you typically won't create Router instances directly.
        Instead, you'll receive them from RouterClient methods and use them in other SDK operations.
    """

    id: str = dataclasses.field(init=False)
    version: int
    description: str
    createTime: str
    name: str
    routerSpec: Dict[str, Any]

    def __post_init__(self):
        """Extract the router ID from the full resource name and set the `id` field.
        
        The ID is taken from the last segment of the name path. For example, from
        "organizations/org-123/routers/my-router", the ID would be "my-router".
        """
        # Set id as the last segment after the last "/"
        _id = self.name.rsplit("/", 1)[-1]
        object.__setattr__(self, "id", _id) 