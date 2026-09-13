# ResiliChain AI

**A multi-agent autonomous retail supply-chain recovery control tower.**

ResiliChain AI is a starter implementation for Tech Zephyr 4.0's Autonomous Retail Supply Chain Recovery problem. It demonstrates the full agentic loop:

`Goal → Observe → Decide → Act → Verify → Replan → Outcome`

## Why this is agentic

- Five components have distinct, bounded responsibilities.
- Agents inspect persistent environment state and call deterministic tools.
- The selected action changes the digital-twin state.
- A forced carrier failure is observed at runtime.
- The orchestrator replans instead of returning a static answer.
- A separate verifier checks service, cost, time, carbon, and state-change constraints.

## Quick start

### Windows — easiest demo start

Double-click `start_demo.bat`, or run:

```powershell
.\start_demo.bat
```

Then open `http://127.0.0.1:8080`.

### macOS / Linux

```bash
chmod +x start_demo.sh
./start_demo.sh
```

Open `http://127.0.0.1:8080` and click **Run live recovery**. No API key is
required for the included deterministic multi-agent demonstration.

### Docker

```bash
docker compose up --build
```

For the exact demo flow, troubleshooting, and Cloud Run deployment commands, see
[`docs/DEMO_AND_DEPLOY.md`](docs/DEMO_AND_DEPLOY.md).

## API

- `GET /api/health`
- `GET /api/scenarios/port-closure-001`
- `POST /api/scenarios/port-closure-001/reset`
- `POST /api/scenarios/port-closure-001/recover`
- `GET /docs` for interactive OpenAPI documentation

## Test

```bash
pytest -q
```

Tests verify that the orchestrator observes an execution-time carrier failure, replans, selects a different feasible route, persists the new state, and passes every objective constraint.

## Team collaboration

See [`docs/GITHUB_COLLABORATION.md`](docs/GITHUB_COLLABORATION.md) for the repository setup,
collaborator invitation, branch, commit, pull-request, and merge workflow.

## Repository structure

```text
backend/app/       Digital twin, agents, orchestration and API
frontend/          Premium control-tower operations dashboard
tests/             Adaptation, constraint and persistence tests
docs/              Product and architecture documentation
.github/workflows/ Continuous integration
```

## Next implementation milestones

1. Replace weighted enumeration with Google OR-Tools.
2. Add OpenAI Agents SDK orchestration and GPT decision explanations.
3. Add demand, vendor, inventory and shipment event simulators.
4. Introduce human approval for purchases and vendor commitments.
5. Migrate production state, authentication, audit events and live updates to Supabase.
6. Add n8n webhooks for event ingestion and approved notifications.
7. Deploy the container to Cloud Run.
8. Build an evaluation set with at least 30 disruption scenarios.

The current starter is deliberately deterministic and does not require an API key. The
five roles are real, separate Python components with bounded responsibilities; model-backed
reasoning is the next implementation phase, not a mocked claim in this release.

Never commit secrets. Use `.env.example` as the configuration template.
