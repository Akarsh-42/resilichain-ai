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

