# ResiliChain AI

**A guarded multi-agent retail supply-chain recovery control tower.**

ResiliChain AI demonstrates the complete agentic loop:

`Goal → Observe → Decide → LLM critique → Act → Verify → Replan → Outcome`

## Why this is genuinely agentic

- Six agents have distinct, bounded responsibilities.
- Agents inspect persistent digital-twin state and call deterministic tools.
- A live LLM Risk Reasoning Agent critiques plans and explains residual risk.
- The optimizer—not the LLM—enforces cost, SLA, inventory, and carbon constraints.
- The selected action changes the environment state.
- A forced carrier failure is observed at runtime.
- The orchestrator replans and independently verifies the final outcome.

## Run it now

### Windows

1. Double-click `configure_llm.bat` once and follow the two-window instructions.
2. Paste the Groq key after `GROQ_API_KEY=` in Notepad and save.
3. Double-click `start_demo.bat`.
4. Open <http://127.0.0.1:8080> and click **Run live recovery**.

The dashboard must show **LIVE LLM · openai/gpt-oss-20b** before recording the
LLM-enabled demo. If the key is missing or the API is unavailable, the workflow
still completes safely and displays **LLM FALLBACK** honestly.

### macOS / Linux

```bash
cp .env.example .env
# Add GROQ_API_KEY to .env
chmod +x start_demo.sh
./start_demo.sh
```

## Share instantly without cloud deployment

Keep the local server running, install `cloudflared`, then run:

```bash
cloudflared tunnel --url http://127.0.0.1:8080
```

On Windows, double-click `share_demo.bat`. Share the generated
`https://...trycloudflare.com` URL. No Cloudflare account, domain, or billing
setup is required for this temporary demo tunnel.

## Free public deployment on Render

[Deploy to Render](https://render.com/deploy?repo=https://github.com/Akarsh-42/resilichain-ai)

The included `render.yaml` configures the service. One teammate connects the
GitHub repository, selects the free plan, enters `GROQ_API_KEY` as a secret, and
deploys. Everyone else only needs the resulting public URL.

See [`docs/DEMO_AND_DEPLOY.md`](docs/DEMO_AND_DEPLOY.md) for the exact walkthrough.

## API

- `GET /api/health`
- `GET /api/config` — exposes model name and whether live LLM mode is enabled
- `GET /api/scenarios/port-closure-001`
- `POST /api/scenarios/port-closure-001/reset`
- `POST /api/scenarios/port-closure-001/recover`
- `GET /docs` — interactive OpenAPI documentation

## Test

```bash
python -m pytest -q
```

## Repository structure

```text
backend/app/       Digital twin, six agents, orchestration, LLM adapter and API
frontend/          Premium control-tower operations dashboard
tests/             Adaptation, constraints, LLM and persistence tests
docs/              Product, architecture and demo documentation
.github/workflows/ Continuous integration
```

Never commit `.env`, API keys, passwords, or tokens. The repository contains only
`.env.example`; deployment secrets remain in Render's environment settings.
