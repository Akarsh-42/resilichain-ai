from __future__ import annotations

from copy import deepcopy

from .models import Candidate, Disruption, RecoveryPlan, ScenarioState
from .scenarios import port_closure_scenario
from .store import StateStore


class SupplyChainEnvironment:
    """A small digital twin that exposes observable, state-changing tools."""

    def __init__(self, store: StateStore) -> None:
        self.store = store

    def reset(self, scenario_id: str = "port-closure-001") -> ScenarioState:
        if scenario_id != "port-closure-001":
            raise ValueError(f"Unknown scenario: {scenario_id}")
        state = port_closure_scenario()
        self.store.save(state)
        return state

    def observe(self, scenario_id: str) -> ScenarioState:
        state = self.store.get(scenario_id)
        return state if state else self.reset(scenario_id)

    def candidates(self, state: ScenarioState) -> list[Candidate]:
        constraints = state.constraints
        candidates: list[Candidate] = []
        nodes = {node.id: node for node in state.nodes}

        for route in state.routes:
            source = nodes[route.source_id]
            available_inventory = source.inventory.get(constraints.sku, 0)
            violations: list[str] = []
            if not route.available:
                violations.append("route_unavailable")
            if available_inventory < constraints.required_units:
                violations.append("insufficient_inventory")
            if route.capacity_units < constraints.required_units:
                violations.append("insufficient_route_capacity")
            if route.cost > constraints.maximum_cost:
                violations.append("budget_exceeded")
            if route.delivery_hours > constraints.deadline_hours:
                violations.append("deadline_missed")
            if route.carbon_kg > constraints.maximum_carbon_kg:
                violations.append("carbon_cap_exceeded")

            candidates.append(
                Candidate(
                    route_id=route.id,
                    source_id=route.source_id,
                    units=constraints.required_units,
                    cost=route.cost,
                    delivery_hours=route.delivery_hours,
                    carbon_kg=route.carbon_kg,
                    feasible=not violations,
                    violations=violations,
                )
            )
        return candidates

    def execute(self, scenario_id: str, plan: RecoveryPlan) -> tuple[bool, ScenarioState, str]:
        state = deepcopy(self.observe(scenario_id))
        route = next(route for route in state.routes if route.id == plan.route_id)

        if (
            route.id in state.fail_once_route_ids
            and route.id not in state.consumed_failures
        ):
            route.available = False
            state.consumed_failures.append(route.id)
            state.disruptions.append(
                Disruption(
                    id=f"d-runtime-{state.revision + 1}",
                    kind="carrier_breakdown",
                    target_id=route.id,
                    description="Carrier telemetry reported a breakdown during dispatch.",
                )
            )
            state.revision += 1
            state.status = "replanning"
            self.store.save(state)
            return False, state, "Execution failed: selected carrier became unavailable."

        source = next(node for node in state.nodes if node.id == plan.source_id)
        destination = next(node for node in state.nodes if node.id == state.destination_id)
        sku = state.constraints.sku
        source.inventory[sku] -= plan.units
        destination.inventory[sku] = destination.inventory.get(sku, 0) + plan.units
        state.last_action = plan.model_dump()
        state.revision += 1
        state.status = "recovered"
        self.store.save(state)
        return True, state, "Recovery action executed in the simulated environment."

