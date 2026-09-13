# Demo and deployment guide

This guide gets the complete ResiliChain AI demonstration running without an API
key. The included scenario is deterministic so the live demo remains reliable.

## What the live demo proves

The five specialist agents execute a real state-changing workflow:

1. The **Observer Agent** reads the digital twin and detects the east route closure.
2. The **Candidate Agent** constructs and validates recovery options.
3. The **Optimizer Agent** selects the west-road plan against cost, SLA, carbon,
   inventory, and service constraints.
4. The **Execution Agent** calls the carrier tool. A forced carrier failure occurs.
5. The **Orchestrator** observes the failure and requests a new plan.
6. The agents select and dispatch the south-express route.
7. The **Verifier Agent** independently checks the persisted result.

This demonstrates `Goal → Observe → Decide → Act → Evaluate → Adapt → Outcome`.

## Run now on Windows

Prerequisite: install Python 3.11 or newer and make sure `py` or `python` works in
Command Prompt.

From File Explorer, double-click `start_demo.bat`. Or open PowerShell in the
project folder and run:

```powershell
.\start_demo.bat
```

Open `http://127.0.0.1:8080`. The first launch can take a minute while Python
packages are installed.

## Run on macOS or Linux

```bash
chmod +x start_demo.sh
./start_demo.sh
```

Open `http://127.0.0.1:8080`.

## Demo script for the judges

1. Point out the P1 disruption, five agents, live route map, and constraints.
2. Click **Run live recovery**.
3. Explain the first decision while the trace shows the west-road selection.
4. Highlight the simulated carrier rejection and automatic replanning.
5. Show south-express selected in the decision matrix.
6. Finish on the verified outcome and open one evidence panel in the trace.
7. Optionally click **Export run** to download the auditable JSON evidence.

Use **Reset scenario** before repeating the demo. Press `R` as a keyboard shortcut
to start a recovery run.

## Run with Docker

```bash
docker compose up --build
```

Open `http://127.0.0.1:8080`. Stop it with `Ctrl+C`.

## Deploy to Google Cloud Run

The repository contains a production-compatible `Dockerfile`. Install the Google
Cloud CLI, enable billing for a project, then run these commands from the project
folder:

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud run deploy resilichain-ai --source . --region asia-south1 --allow-unauthenticated
```

Choose `Y` if the CLI asks to enable an API. When deployment completes, the CLI
prints the public HTTPS URL. The `--source .` command uses the included Dockerfile.

For this hackathon demo, SQLite lives in the container filesystem. Cloud Run's
container filesystem is ephemeral, so a new instance can begin with a fresh demo
state. That is acceptable for the resettable demonstration. Use Supabase/Postgres
before relying on durable production data.

## Fast troubleshooting

| Symptom | Fix |
| --- | --- |
| `python` or `py` not found | Install Python 3.11+ and enable “Add Python to PATH”. |
| Port 8080 already in use | Stop the old server, or change `--port 8080` to `--port 8081`. |
| Blank/stale dashboard | Hard refresh with `Ctrl+Shift+R`. |
| Demo already completed | Click **Reset scenario**, then run it again. |
| Cloud deploy permission error | Confirm billing, project ownership, and Cloud Run/Cloud Build roles. |

## Health checks

- Dashboard: `http://127.0.0.1:8080`
- API health: `http://127.0.0.1:8080/api/health`
- Interactive API docs: `http://127.0.0.1:8080/docs`
