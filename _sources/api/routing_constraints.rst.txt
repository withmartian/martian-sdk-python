Routing Constraints
==================

.. currentmodule:: martian_apart_hack_sdk.models.RouterConstraints

When using a router, you need to specify a ``RoutingConstraint`` to determine which point on the Pareto frontier to use.
To create a ``RoutingConstraint``, pass in a ``CostConstraint`` or ``QualityConstraint`` object.
To create a ``CostConstraint`` or ``QualityConstraint``, pass in a ``ConstraintValue`` object.

.. autoclass:: RoutingConstraint
   :members:
   :exclude-members: to_dict

.. autoclass:: CostConstraint
   :members:
   :exclude-members: to_dict

.. autoclass:: QualityConstraint
   :members:
   :exclude-members: to_dict

.. autoclass:: ConstraintValue
   :members:
   :exclude-members: to_dict




