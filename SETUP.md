# SETUP: Standbai Backend API

## Prerequisites
- **Python 3.12 or newer.** The test suite passed on Python 3.14 on 2026-10-10. The Docker image uses 3.12.
- pip and `venv`.
- Optional: a **NASA FIRMS MAP_KEY** (free, https://firms.modaps.eosdis.nasa.gov/api/map_key/) for live fire data.

## Install and run

```bash
git clone https://github.com/ITHACKITS/BE-FORGEHACK-2026.git
cd BE-FORGEHACK-2026
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --env-file .env
```

- API: http://127.0.0.1:8000
- Interactive docs: http://127.0.0.1:8000/docs
- On first start, the app creates the SQLite schema and seeds the database if it's empty.

> The code doesn't load `.env` by itself yet (ticket BE-02), so pass `--env-file .env` to uvicorn or export the variables.

## Environment variables

**Read by the code on `main` today:**

| Variable | Default | Purpose |
|---|---|---|
| `UDARASIAGA_OFFLINE` | `1` | `1` blocks all network calls and uses only `data/`. Set `0` to use live sources. Becomes `STANDBAI_OFFLINE` in BE-02. |
| `FIRMS_MAP_KEY` | - | NASA FIRMS API key |
| `OPENAQ_API_KEY` | - | OpenAQ (validation scripts) |
| `GEMINI_API_KEY` | - | Used by the emergency advisory until BE-04 moves it to the AI service |

**Added by the PRD tickets** (see `PRD.md` §4.2): `STANDBAI_OFFLINE`, `AI_SERVICE_URL`, `AI_INTERNAL_TOKEN`, `JOB_TOKEN`, `N8N_ALERT_WEBHOOK_URL`, `N8N_WEBHOOK_SECRET`, `CORS_ORIGINS`, `PUBLIC_APP_URL`.

> `.env.example` on `main` still lists names that the code doesn't read (`APP_NAME`, `DATABASE_URL`, `AI_SERVICE_URL`). BE-02 aligns it.

Never commit `.env`. If an API key was ever pasted into a chat or an issue, rotate it.

## Tests and lint

```bash
UDARASIAGA_OFFLINE=1 python -m pytest -q   # 40 passed on 2026-10-10
ruff check .
```

## Useful scripts

| Command | Purpose |
|---|---|
| `python -m scripts.db.seed_database` | Re-seed `data/udarasiaga.db` from `data/layers` and `data/events` |
| `python scripts/generators/download_firms.py` | Download FIRMS hotspots (needs `FIRMS_MAP_KEY`, offline off) |
| `python scripts/generators/snapshot_ensemble.py` | Save the current Open-Meteo ensemble for an event |
| `python scripts/verification/check_sources.py` | Check that the data sources respond; updates `docs/SOURCES.md` |
| `python scripts/validate_live_api.py` | Smoke test against a running API |

Run scripts from the repository root so that `app` is importable.

## Deploy to Google Cloud Run (ticket BE-01)
1. Install the gcloud CLI, run `gcloud auth login`, and select a project with billing enabled.
2. Create a `Dockerfile` and `.dockerignore` as in `PRD.md` §4.10.
3. Create the secrets:
   ```bash
   printf '%s' "$FIRMS_MAP_KEY" | gcloud secrets create firms-map-key --data-file=-
   printf '%s' "$(openssl rand -hex 24)" | gcloud secrets create job-token --data-file=-
   printf '%s' "$(openssl rand -hex 24)" | gcloud secrets create ai-internal-token --data-file=-
   ```
4. Deploy:
   ```bash
   gcloud run deploy standbai-api --source . --region asia-southeast2 \
     --cpu 1 --memory 2Gi --no-cpu-throttling --min-instances 1 --max-instances 1 --timeout 300 \
     --allow-unauthenticated \
     --set-env-vars STANDBAI_OFFLINE=0,AI_SERVICE_URL=<ai-url>,CORS_ORIGINS=<vercel-url>,PUBLIC_APP_URL=<vercel-url> \
     --set-secrets FIRMS_MAP_KEY=firms-map-key:latest,AI_INTERNAL_TOKEN=ai-internal-token:latest,JOB_TOKEN=job-token:latest
   ```
5. Check `curl <url>/health` and open `<url>/docs`. Share the URL with the frontend (`VITE_API_BASE_URL`) and AI teams.

## n8n and the Telegram bot (ticket BE-11)
1. Redeem the ForgeHacks **n8n Cloud Pro** perk (Discord) and open your n8n workspace.
2. Create a bot with **@BotFather** (`/newbot`). Store the token only as an n8n **Telegram credential**.
3. In n8n, create an HTTP header credential `X-Job-Token: <job-token>`.
4. Build or import the workflows from `n8n/`:
   - `standbai-refresh-fires`;
   - `standbai-refresh-air`;
   - `standbai-telegram-bot`;
   - `standbai-daily-digest`;
   - P1: `standbai-alert-webhook`.
   Point their HTTP nodes at the Cloud Run URL.
5. P1: copy the Webhook node URL of `standbai-alert-webhook` into `N8N_ALERT_WEBHOOK_URL`, choose a secret for `N8N_WEBHOOK_SECRET`, and redeploy.
6. Test in Telegram: `/start`, `/subscribe Pekanbaru`, `/status Jambi`, `/unsubscribe`.
7. Export every workflow (**⋯ → Download**) into `n8n/` and commit it, after checking that the exports contain no tokens.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Live data never loads | `UDARASIAGA_OFFLINE` defaults to `1`; set it to `0` |
| Variables in `.env` are ignored | Use `--env-file .env` until BE-02 adds `load_dotenv()` |
| CORS error from the web app | Add the web origin to `CORS_ORIGINS` (after BE-02; today CORS allows `*`) |
| Simulations stall on Cloud Run | Deploy with `--no-cpu-throttling` |
| Runs disappear after a redeploy | Expected: runs live on the instance disk; re-run or use the presets |
| `pip install` fails on geo packages | Use Python 3.12 or 3.14 with a recent pip; `pip install --upgrade pip` first |
