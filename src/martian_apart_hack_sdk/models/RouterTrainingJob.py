"""Router training job model."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass(frozen=True)
class RouterTrainingJob:
    """Represents a router training job response."""
    
    name: str
    router_name: str
    judge_name: str
    judge_version: int
    status: str
    create_time: datetime
    update_time: datetime
    llms: List[str]
    error_message: Optional[str]
    retry_count: int

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
            error_message=data.get("errorMessage"),
            retry_count=data.get("retryCount", 0)
        ) 
