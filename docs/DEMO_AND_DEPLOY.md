# Live LLM demo and easy deployment

## Important model choice

ChatGPT Plus and the OpenAI API are separate products, so Plus does not provide
an API key for this backend. ResiliChain therefore uses Groq's OpenAI-compatible
API with the production model `openai/gpt-oss-20b`.

The architecture is deliberately guarded:

- The LLM Risk Reasoning Agent critiques and explains a selected plan.
- Deterministic agents enforce hard constraints and execute tools.
- If the model times out, the workflow continues with an explicit fallback.
- The dashboard always labels whether a real LLM response was used.

## Configure the live LLM

On Windows, double-click `configure_llm.bat`. It opens both the Groq API-key
page and the correct local `.env` file in Notepad. Paste the key after
`GROQ_API_KEY=`, save, and close Notepad.

The equivalent manual configuration is:

```dotenv
GROQ_API_KEY=paste_your_key_here
LLM_MODEL=openai/gpt-oss-20b
```

Do not send the key to teammates and never commit `.env`.

## Run on Windows

Double-click `start_demo.bat`, or run:

```powershell
.\start_demo.bat
```

Open <http://127.0.0.1:8080>. Confirm the top-right badge says **LIVE LLM**.
The first launch can take a minute while dependencies install.

## What the judge will see

1. The Disruption Intelligence Agent observes the east-port closure.
2. The Inventory & Sourcing Agent builds four recovery candidates.
3. The Recovery Optimization Agent selects the best feasible route.
4. The LLM Risk Reasoning Agent critiques the plan using live model inference.
5. The first carrier call fails at runtime.
6. The Control Tower Orchestrator observes the failure and replans.
7. The new route executes and changes inventory in the digital twin.
8. The Outcome Verification Agent independently checks five constraints.

Open **Inspect evidence** under the LLM trace. It shows `llm_used: true`, the
provider, and the exact model ID. That is proof that a live LLM participated.

## Option A — instant public link, no cloud account

This is best for an immediate teammate review or live judging session.

1. Keep `start_demo.bat` running.
2. Install `cloudflared` from the official Cloudflare download page.
3. Double-click `share_demo.bat`, or run:

```bash
cloudflared tunnel --url http://127.0.0.1:8080
```

4. Share the printed `https://...trycloudflare.com` address.

The link works only while both terminal windows and your laptop remain online.
It is a temporary testing tunnel, not permanent hosting.

## Option B — free public Render deployment

Open:

<https://render.com/deploy?repo=https://github.com/Akarsh-42/resilichain-ai>

Then:

1. Sign in to Render using GitHub.
2. Connect `Akarsh-42/resilichain-ai`.
3. Render reads the included `render.yaml`.
4. Choose the **Free** instance.
5. Paste the Groq key into the requested `GROQ_API_KEY` secret field.
6. Click **Deploy Blueprint**.
7. Share the resulting `https://resilichain-ai-....onrender.com` URL.

Only the repository owner/deployer needs a Render account. Friends and judges
simply open the public URL.

Free Render services can sleep after inactivity, so open the URL a few minutes
before presenting. The SQLite demo state is intentionally resettable and may be
cleared when a free instance restarts.

## Demo narration

> ResiliChain is a six-agent control tower, not a chatbot. The deterministic
> agents observe state, generate candidates, optimize constraints, execute tools,
> and verify outcomes. A live GPT-OSS reasoning agent critiques each operational
> plan. When the selected carrier unexpectedly fails, the orchestrator observes
> the changed environment and replans to a new feasible route.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Badge says `LLM FALLBACK` | Confirm `.env` exists, the Groq key is correct, then restart the server. |
| `python` or `py` not found | Install Python 3.11+ and enable “Add Python to PATH”. |
| Port 8080 already in use | Stop the old server or change the launcher to port 8081. |
| Render loads slowly | Free services sleep; visit the URL several minutes before judging. |
| Tunnel command not found | Install `cloudflared`, reopen Command Prompt, and retry. |
| Scenario already completed | Click **Reset scenario** before another run. |

Health endpoints: `/api/health`, `/api/config`, and `/docs`.
