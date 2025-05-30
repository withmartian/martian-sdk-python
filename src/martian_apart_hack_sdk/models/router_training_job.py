"""Router training job model."""

import dataclasses
import datetime as dt
from typing import Any, Dict, List


@dataclasses.dataclass(frozen=True)
class RouterTrainingJob:
    """Represents a router training job response."""

    name: str
    router_name: str
    judge_name: str
    judge_version: int
    status: str
    create_time: dt.datetime
    update_time: dt.datetime
    llms: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RouterTrainingJob":
        """Create a RouterTrainingJob instance from a dictionary.

        Args:
            data: Dictionary containing the training job data

        Returns:
            RouterTrainingJob instance
        """
        return cls(
            name=data["name"],
            router_name=data["routerName"],
            judge_name=data["judgeName"],
            judge_version=data["judgeVersion"],
            status=data["status"],
            create_time=data["createTime"],
            update_time=data["updateTime"],
            llms=data["llms"],
        )
