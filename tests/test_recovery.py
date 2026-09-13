import json
from io import BytesIO

from backend.app.agents import LLMReasoningAgent, OptimizationAgent
from backend.app.environment import SupplyChainEnvironment
from backend.app.orchestrator import ControlTowerOrchestrator
from backend.app.store import StateStore


def build_system(tmp_path):
    store = StateStore(tmp_path / "test.db")
    environment = SupplyChainEnvironment(store)
    environment.reset()
    return store, environment, ControlTowerOrchestrator(environment)


def test_agent_replans_after_runtime_failure(tmp_path):
    _, _, orchestrator = build_system(tmp_path)
    result = orchestrator.recover("port-closure-001")

    assert result.status == "resolved"
    assert result.attempts == 2
    assert result.final_plan is not None
    assert result.final_plan.route_id == "south-express"
    assert result.verification is not None
    assert result.verification.passed is True
    assert any(trace.action == "replan" for trace in result.traces)


def test_recovery_respects_every_constraint(tmp_path):
    _, _, orchestrator = build_system(tmp_path)
    result = orchestrator.recover("port-closure-001")
    checks = result.verification.checks

    assert checks["inventory_restored"]
    assert checks["within_budget"]
    assert checks["within_deadline"]
    assert checks["within_carbon_cap"]
    assert checks["state_changed"]


def test_state_is_persistent(tmp_path):
    store, environment, orchestrator = build_system(tmp_path)
    result = orchestrator.recover("port-closure-001")
    reloaded = StateStore(store.database_path).get("port-closure-001")

    assert reloaded is not None
    assert reloaded.revision == result.state.revision
    assert reloaded.status == "recovered"
    assert reloaded.last_action["route_id"] == "south-express"


def test_recovery_exposes_honest_llm_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    _, _, orchestrator = build_system(tmp_path)
    result = orchestrator.recover("port-closure-001")
    reasoning_traces = [
        trace for trace in result.traces if trace.action == "reason_about_plan"
    ]

    assert reasoning_traces
    assert reasoning_traces[0].evidence["llm_used"] is False
    assert reasoning_traces[0].evidence["fallback_reason"]


def test_llm_reasoning_agent_records_live_model_evidence(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    store = StateStore(tmp_path / "llm.db")
    environment = SupplyChainEnvironment(store)
    state = environment.reset()
    candidates = environment.candidates(state)
    plan = OptimizationAgent().select(candidates, state)
    payload = {
        "choices": [
            {
                "message": {
                    "content": "The route satisfies the limits. Verify carrier telemetry before closure."
                }
            }
        ]
    }
    monkeypatch.setattr(
        "backend.app.agents.urlopen",
        lambda request, timeout: BytesIO(json.dumps(payload).encode("utf-8")),
    )

    evidence = LLMReasoningAgent().critique(state, candidates, plan, attempt=1)

    assert evidence["llm_used"] is True
    assert evidence["provider"] == "Groq"
    assert evidence["model"] == "openai/gpt-oss-20b"
