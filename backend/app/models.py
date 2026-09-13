from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    WAREHOUSE = "warehouse"
    STORE = "store"


class SupplyNode(BaseModel):
    id: str
    name: str
    node_type: NodeType
    inventory: dict[str, int]
    latitude: float
    longitude: float


class Route(BaseModel):
    id: str
    source_id: str
    destination_id: str
    mode: str
    capacity_units: int
    cost: float
    delivery_hours: float
    carbon_kg: float
    available: bool = True


class ConstraintSet(BaseModel):
    sku: str
    required_units: int
    deadline_hours: float
    maximum_cost: float
    maximum_carbon_kg: float


class Disruption(BaseModel):
    id: str
    kind: str
    target_id: str
    description: str
    active: bool = True


class ScenarioState(BaseModel):
    scenario_id: str
    title: str
    objective: str
    destination_id: str
    constraints: ConstraintSet
    nodes: list[SupplyNode]
    routes: list[Route]
    disruptions: list[Disruption] = Field(default_factory=list)
    fail_once_route_ids: list[str] = Field(default_factory=list)
    consumed_failures: list[str] = Field(default_factory=list)
    revision: int = 0
    status: str = "disrupted"
    last_action: dict[str, Any] | None = None


class Candidate(BaseModel):
    route_id: str
    source_id: str
    units: int
    cost: float
    delivery_hours: float
    carbon_kg: float
    feasible: bool
    violations: list[str] = Field(default_factory=list)
    score: float | None = None


class RecoveryPlan(BaseModel):
    route_id: str
    source_id: str
    units: int
    expected_cost: float
    expected_delivery_hours: float
    expected_carbon_kg: float
    score: float
    rationale: str


class AgentTrace(BaseModel):
    sequence: int
    agent: str
    action: str
    summary: str
    evidence: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    passed: bool
    checks: dict[str, bool]
    explanation: str


class RecoveryRun(BaseModel):
    run_id: str
    scenario_id: str
    status: str
    attempts: int
    final_plan: RecoveryPlan | None
    verification: VerificationResult | None
    traces: list[AgentTrace]
    state: ScenarioState

