from __future__ import annotations

from uuid import uuid4

from .agents import (
    DisruptionIntelligenceAgent,
    LLMReasoningAgent,
    OptimizationAgent,
    SourcingAgent,
    VerificationAgent,
)
from .environment import SupplyChainEnvironment
from .models import AgentTrace, RecoveryRun


class ControlTowerOrchestrator:
    name = "Control Tower Orchestrator"

    def __init__(self, environment: SupplyChainEnvironment) -> None:
        self.environment = environment
        self.disruption_agent = DisruptionIntelligenceAgent()
        self.sourcing_agent = SourcingAgent()
        self.optimization_agent = OptimizationAgent()
        self.reasoning_agent = LLMReasoningAgent()
        self.verification_agent = VerificationAgent()

    def recover(self, scenario_id: str, maximum_attempts: int = 3) -> RecoveryRun:
        traces: list[AgentTrace] = []

        def trace(agent: str, action: str, summary: str, evidence: dict | None = None) -> None:
            traces.append(
                AgentTrace(
                    sequence=len(traces) + 1,
                    agent=agent,
                    action=action,
                    summary=summary,
                    evidence=evidence or {},
                )
            )

        state = self.environment.observe(scenario_id)
        trace(self.name, "set_goal", state.objective, {"revision": state.revision})

        final_plan = None
        verification = None

        for attempt in range(1, maximum_attempts + 1):
            intelligence = self.disruption_agent.analyze(state)
            trace(
                self.disruption_agent.name,
                "observe_environment",
                f"Found {len(intelligence['active_disruptions'])} active disruption(s).",
                intelligence,
            )

            candidates = self.sourcing_agent.propose(self.environment, state)
            trace(
                self.sourcing_agent.name,
                "build_candidates",
                f"Generated {len(candidates)} alternatives; "
                f"{sum(candidate.feasible for candidate in candidates)} are feasible.",
                {"candidates": [candidate.model_dump() for candidate in candidates]},
            )

            plan = self.optimization_agent.select(candidates, state)
            if plan is None:
                trace(
                    self.optimization_agent.name,
                    "escalate",
                    "No feasible option satisfies all objective constraints.",
                )
                return RecoveryRun(
                    run_id=str(uuid4()),
                    scenario_id=scenario_id,
                    status="human_review",
                    attempts=attempt,
                    final_plan=None,
                    verification=None,
                    traces=traces,
                    state=state,
                )

            final_plan = plan
            trace(
                self.optimization_agent.name,
                "select_plan",
                f"Selected route {plan.route_id} with score {plan.score}.",
                plan.model_dump(),
            )

            critique = self.reasoning_agent.critique(
                state=state,
                candidates=candidates,
                plan=plan,
                attempt=attempt,
            )
            trace(
                self.reasoning_agent.name,
                "reason_about_plan",
                critique["analysis"],
                critique,
            )

            executed, state, message = self.environment.execute(scenario_id, plan)
            trace(self.name, "execute_action", message, {"route_id": plan.route_id})

            if not executed:
                trace(
                    self.name,
                    "replan",
                    "Observed execution failure; refreshing state and selecting another option.",
                    {"next_attempt": attempt + 1},
                )
                continue

            verification = self.verification_agent.verify(state, plan)
            trace(
                self.verification_agent.name,
                "verify_outcome",
                verification.explanation,
                verification.model_dump(),
            )

            if verification.passed:
                return RecoveryRun(
                    run_id=str(uuid4()),
                    scenario_id=scenario_id,
                    status="resolved",
                    attempts=attempt,
                    final_plan=final_plan,
                    verification=verification,
                    traces=traces,
                    state=state,
                )

            trace(self.name, "replan", "Verification failed; starting another attempt.")

        return RecoveryRun(
            run_id=str(uuid4()),
            scenario_id=scenario_id,
            status="human_review",
            attempts=maximum_attempts,
            final_plan=final_plan,
            verification=verification,
            traces=traces,
            state=state,
        )
