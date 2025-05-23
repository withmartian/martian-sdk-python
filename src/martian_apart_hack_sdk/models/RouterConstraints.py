"""Router constraints models."""

import dataclasses
from typing import Optional, Union, Literal


@dataclasses.dataclass
class ConstraintValue:
    """Value for a constraint that can be either numeric or a model name."""
    numeric_value: Optional[float] = None
    model_name: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format expected by the API."""
        if self.numeric_value is not None:
            return {"numeric_value": self.numeric_value}
        if self.model_name is not None:
            return {"model_name": self.model_name}
        raise ValueError("Either numeric_value or model_name must be set")


@dataclasses.dataclass
class CostConstraint:
    """Cost constraint for routing."""
    value: ConstraintValue

    def to_dict(self) -> dict:
        """Convert to dictionary format expected by the API."""
        return self.value.to_dict()


@dataclasses.dataclass
class QualityConstraint:
    """Quality constraint for routing."""
    value: ConstraintValue

    def to_dict(self) -> dict:
        """Convert to dictionary format expected by the API."""
        return self.value.to_dict()


@dataclasses.dataclass
class RoutingConstraint:
    """Routing constraint that can be either a cost or quality constraint."""
    cost_constraint: Optional[CostConstraint] = None
    quality_constraint: Optional[QualityConstraint] = None

    def to_dict(self) -> dict:
        """Convert to dictionary format expected by the API."""
        result = {}
        if self.cost_constraint is not None:
            result["cost_constraint"] = self.cost_constraint.to_dict()
        if self.quality_constraint is not None:
            result["quality_constraint"] = self.quality_constraint.to_dict()
        if not result:
            raise ValueError("At least one constraint must be set")
        return result 