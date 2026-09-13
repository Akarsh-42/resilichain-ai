from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

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


class LLMReasoningAgent:
    """Critiques plans with a live LLM without bypassing hard constraints."""

    name = "LLM Risk Reasoning Agent"

    def __init__(self) -> None:
        self.provider = "Groq"
        self.model = os.getenv("LLM_MODEL", "openai/gpt-oss-20b")
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.base_url = os.getenv(
            "GROQ_BASE_URL", "https://api.groq.com/openai/v1"
        ).rstrip("/")
        try:
            self.timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "10"))
        except ValueError:
            self.timeout_seconds = 10.0

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def critique(
        self,
        state: ScenarioState,
        candidates: list[Candidate],
        plan: RecoveryPlan,
        attempt: int,
    ) -> dict:
        prompt_payload = {
            "goal": state.objective,
            "attempt": attempt,
            "active_disruptions": [
                disruption.model_dump()
                for disruption in state.disruptions
                if disruption.active
            ],
            "hard_constraints": state.constraints.model_dump(),
            "candidates": [candidate.model_dump() for candidate in candidates],
            "selected_plan": plan.model_dump(),
        }

        if not self.enabled:
            return self._fallback(plan, candidates, "GROQ_API_KEY is not configured")

        request_body = {
            "model": self.model,
            "temperature": 0.1,
            "max_completion_tokens": 180,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the risk reasoning specialist inside an autonomous retail "
                        "supply-chain control tower. Critique the optimizer's selected plan "
                        "in two concise sentences. Explain why it is defensible, name the "
                        "most important residual risk, and state whether human review is "
                        "needed. Never invent values or change the selected route."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt_payload, separators=(",", ":")),
                },
            ],
        }
        request = Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(request_body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
            analysis = payload["choices"][0]["message"]["content"].strip()
            if not analysis:
                raise ValueError("The model returned an empty response")
            return {
                "llm_used": True,
                "provider": self.provider,
                "model": self.model,
                "analysis": analysis,
                "fallback_reason": None,
            }
        except (
            HTTPError,
            URLError,
            TimeoutError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            return self._fallback(plan, candidates, type(exc).__name__)

    def _fallback(
        self, plan: RecoveryPlan, candidates: list[Candidate], reason: str
    ) -> dict:
        rejected = sum(not candidate.feasible for candidate in candidates)
        return {
            "llm_used": False,
            "provider": self.provider,
            "model": self.model,
            "analysis": (
                f"Guarded fallback confirms {plan.route_id} satisfies every hard constraint; "
                f"{rejected} alternative(s) were rejected. Runtime carrier telemetry remains "
                "the primary residual risk, so execution must be verified before closure."
            ),
            "fallback_reason": reason,
        }


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
