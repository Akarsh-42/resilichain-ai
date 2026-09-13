# Build roadmap

## Phase 0 — completed starter

- Synthetic supply-chain digital twin
- Five bounded agent roles
- Persistent SQLite task state
- Cost/time/carbon constraint scoring
- Runtime carrier-failure injection
- Automatic replanning and independent verification
- FastAPI endpoints
- Premium static control-tower dashboard
- Docker and CI configuration
- Adaptation, constraint, and persistence tests

## Phase 1 — credible environment

- Add products, vendors, purchase orders, warehouses, stores, and shipments.
- Add disruption event types: vendor failure, port closure, demand spike, weather delay, and warehouse capacity loss.
- Provide state-changing tools for reroute, reallocate, transfer, and simulated purchase order.
- Record every observation, proposal, action, result, and revision in an immutable audit log.

**Exit test:** ten deterministic scenarios produce reproducible state transitions.

## Phase 2 — optimization layer

- Replace weighted candidate enumeration with Google OR-Tools.
- Support split shipments and multiple-source allocation.
- Implement hard constraints for inventory, capacity, deadline, budget, and carbon.
- Keep LLMs away from arithmetic and constraint enforcement.

**Exit test:** every selected plan is independently constraint-checked and compared with a baseline.

## Phase 3 — model-backed multi-agent reasoning

- Implement the workflow with the OpenAI Agents SDK and explicit agent handoffs.
- Use GPT for event interpretation, evidence requests, plan explanations, and exception handling.
- Keep typed Pydantic contracts between agents.
- Add confidence thresholds, bounded retries, and human approval for purchases or supplier commitments.

**Exit test:** malformed agent outputs are rejected; tool failures trigger bounded recovery or escalation.

## Phase 4 — premium product experience

- Upgrade the dashboard to React/Next.js.
- Add a real interactive network map, scenario builder, constraints panel, comparison table, and live agent trace.
- Show before/after KPIs and why rejected plans violated constraints.
- Add a one-click sample scenario for judges.

**Exit test:** the full required demo can be completed from one screen in under five minutes.

## Phase 5 — integrations and deployment

- Use n8n only for disruption webhooks, scheduled monitoring, and approved email/Slack notifications.
- Use Supabase PostgreSQL for durable state, Auth, audit events, Storage, and dashboard updates.
- Deploy the API/agent service to Cloud Run.
- Add structured logs, traces, health checks, secrets management, and GitHub Actions deployment.
- Maintain a local Docker fallback for live judging.

**Exit test:** hosted and local versions pass the same evaluation suite.

## Phase 6 — evaluation and submission

- Create at least 30 unseen disruption scenarios.
- Measure resolution rate, constraint-violation rate, recovery success, plan regret versus baseline, latency, and model cost.
- Record one normal case and one changed-condition/failure case.
- Finish architecture, README, limitations, acknowledgements, presentation, and 3–5 minute demo.

**Exit test:** no claimed metric appears in the presentation without a reproducible evaluation result.

## Suggested team ownership

| Owner | Workstream |
| --- | --- |
| Member 1 | OpenAI agents, orchestration, model contracts |
| Member 2 | Digital twin, APIs, database, event simulator |
| Member 3 | OR-Tools optimization, constraints, evaluation |
| Member 4 | Frontend, deployment, demo, documentation |
