from __future__ import annotations

from .environment import SupplyChainEnvironment
from .models import Candidate, RecoveryPlan, ScenarioState, VerificationResult


class DisruptionIntelligenceAgent:
    name = "Disruption Intelligence Agent"

    def analyze(self, state: ScenarioState) -> dict:
        unavailable = [route.id for route in state.routes if not route.available]
        return {
            "active_disruptions": [
                disruption.model_dump()
                for disruption in state.disruptions
                if disruption.active
            ],
            "unavailable_routes": unavailable,
            "state_revision": state.revision,
        }


class SourcingAgent:
    name = "Inventory & Sourcing Agent"

    def propose(
        self, environment: SupplyChainEnvironment, state: ScenarioState
    ) -> list[Candidate]:
        return environment.candidates(state)


class OptimizationAgent:
    name = "Recovery Optimization Agent"

    def select(self, candidates: list[Candidate], state: ScenarioState) -> RecoveryPlan | None:
        feasible = [candidate for candidate in candidates if candidate.feasible]
        if not feasible:
            return None

        constraints = state.constraints
        for candidate in feasible:
            candidate.score = round(
                0.45 * (candidate.cost / constraints.maximum_cost)
                + 0.35 * (candidate.delivery_hours / constraints.deadline_hours)
                + 0.20 * (candidate.carbon_kg / constraints.maximum_carbon_kg),
                4,
            )

        selected = min(feasible, key=lambda candidate: candidate.score or 999)
        return RecoveryPlan(
            route_id=selected.route_id,
            source_id=selected.source_id,
            units=selected.units,
            expected_cost=selected.cost,
            expected_delivery_hours=selected.delivery_hours,
            expected_carbon_kg=selected.carbon_kg,
            score=selected.score or 0,
            rationale=(
                "Selected the lowest weighted feasible option across cost (45%), "
                "delivery time (35%), and carbon (20%)."
            ),
        )


class VerificationAgent:
    name = "Outcome Verification Agent"

    def verify(self, state: ScenarioState, plan: RecoveryPlan) -> VerificationResult:
        destination = next(node for node in state.nodes if node.id == state.destination_id)
        constraints = state.constraints
        checks = {
            "inventory_restored": destination.inventory.get(constraints.sku, 0)
            >= 20 + constraints.required_units,
            "within_budget": plan.expected_cost <= constraints.maximum_cost,
            "within_deadline": plan.expected_delivery_hours <= constraints.deadline_hours,
            "within_carbon_cap": plan.expected_carbon_kg <= constraints.maximum_carbon_kg,
            "state_changed": state.revision > 0 and state.last_action is not None,
        }
        passed = all(checks.values())
        return VerificationResult(
            passed=passed,
            checks=checks,
            explanation=(
                "All service, cost, delivery, carbon, and state-change constraints passed."
                if passed
                else "One or more objective constraints failed; replanning is required."
            ),
        )

