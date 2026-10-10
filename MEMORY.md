# MEMORY: StandbAI Backend API (`BE-FORGEHACK-2026`)

> ## Language rule (read first)
> **Always use English** in this repository: code, comments, docstrings, API values and error messages, OpenAPI tags, docs, commit messages, and every explanation written by an AI assistant. ForgeHacks is an international hackathon judged in English.
> Allowed exceptions: stable data slugs (e.g. `hutan_sebangau`, `karhutla_riau`); proper nouns (places; agencies such as BMKG, PVMBG, BPBD, BNPB); official Indonesian terms carried with an English gloss (e.g. ISPU `official_name_id: "Tidak Sehat"` next to `code: "unhealthy"`; "Level III, Siaga (Watch)").

Shared memory for people and coding agents working on the backend. Keep **Progress** and the **Decision log** current. Tasks live in [`PRD.md`](PRD.md); the data model is in [`ERD.md`](ERD.md); datasets are in [`docs/DATASETS.md`](docs/DATASETS.md).

---

## 1. Competition essentials
- **ForgeHacks Online 2026**, track **AI + Climate**: "Build an AI-powered solution that helps people understand environmental changes, prepare for climate impacts, use resources wisely, or create resilient systems."
- **Submission locks Sat Oct 10, 12:00 PM ET = 23:00 WIB.** Feature freeze 18:00 WIB.
- **Judges test the live link.** The API must be deployed, CORS-correct and honest about what is real versus example data.
- **Judging:** impact · technical & AI use ("AI does useful work; explain how and why") · innovation · execution & completeness · presentation, 20% each.
- **Rules:** build during the event; use AI honestly; "a half-working project is okay; overstating it isn't."

## 2. Product
- **StandbAI** tells families in Indonesia where wildfire smoke and volcanic ash will go, and what to prepare before it arrives.
- **This repo is the single public API** for:
  - the web app (`FE-FORGEHACK-2026`);
  - n8n Cloud, which runs the scheduled jobs and the **Telegram bot** (`/subscribe`, `/status`, daily digest, instant alerts).
- **What it owns:**
  - the Lagrangian dispersion engine (ash and smoke, ensemble probability tiers);
  - impact analysis, the spatial database, and city-centred endpoints;
  - the preparedness calculator, subscriptions, and the optional `/chat` orchestration.
- **Honesty rules:** see [`AGENTS.md`](AGENTS.md).
  - ranges, not single impact numbers;
  - labelled assumptions and scenarios;
  - the `is_example` flag;
  - the disclaimer "Not an official warning. Follow BMKG, PVMBG and your local BPBD."

## 3. Architecture
```mermaid
flowchart LR
  FE[Web app · Vercel] --> BE[This API · FastAPI · Cloud Run]
  N8N[n8n Cloud + Telegram bot] <--> BE
  BE --> AI[AI service · Cloud Run]
  BE --> DB[(SQLite + R*Tree)]
  BE --> EXT[Open-Meteo · NASA FIRMS · OSRM · Overpass]
```
- Local ports: BE 8000, AI 8001, FE 5173.

## 4. People
| Person | Role in this repo |
|---|---|
| **Hikari Reiziq** | API and platform: deploy (BE + AI), config, city endpoints, preparedness, alerts, n8n/Telegram, `/chat` |
| **Arya Bisma** | Engine and data: simulation engine, fires, volcanoes, map frames, timeline, history data |
| Ziddan Habibie | Frontend consumer |
| Arkan Zahir | AI service (upstream for chat, advisory, outlook) |

## 5. Repository map
| Path | Contents |
|---|---|
| `app/main.py` | FastAPI app, CORS, routers; seeds the DB on first start |
| `app/api/` | Routers: `health`, `events`, `simulate` (runs, tiers, impact, location cards), `lapis2` (analysis), `lapis3` (trust: validation, limits, sources, export, advisory, evacuation, lahar), `layers`, `attributions` |
| `app/engine/` | Particle engine: `simulator`, `particles` (RK2 advection, settling), `volcano` (eruption source), `fire` (FRP to smoke), `scavenging` (rain), `grid`, `aggregation` (tiers), `landmask` |
| `app/impact/` | Exposure, advisory (deterministic + Gemini), export, routing (OSRM), validation, fire/volcano features |
| `app/ingest/` | FIRMS, Open-Meteo, Overpass, population clients |
| `app/db/` | SQLite connection (WAL), DDL with R*Tree indexes and triggers, repositories |
| `config/` | `assumptions.yaml` (every constant with its status and source), `hazards.yaml` |
| `data/` | `standbai.db`, `events/<id>/` presets, `layers/` GeoJSON, `runs/` outputs (git-ignored) |
| `scripts/` | Data generators, DB seeding, source verification, live API validation, GitHub project-board automation (not used by the app) |
| `tests/` | `test_physics`, `test_integrity`, `test_database`, `test_lapis2`, `test_lapis3` |
| `docs/` | `SPEC.md` (engine spec), `API_CONTRACT.md`, `SOURCES.md`, `DATASETS.md`, `DATABASE_ARCHITECTURE.md` (superseded by `ERD.md`), `fixtures/` |

## 6. Progress (verified on `feat/be-implementation`, 2026-10-10 15:20 WIB)
- **Working, in code:**
  - 31 routes covering simulation runs (volcano and fire), probability tiers per hour, impacts as ranges, facility decision cards, fire-cluster ranking, "extinguish a hotspot", carbon, rain effect, scenario compare, sensitivity, advice, severity, arrival, validation, limits, sources, export, emergency advisory, evacuation route, lahar warning, map layers.
  - DB: 70 volcanoes, 36 forest areas, 992 facilities (583 schools, 330 health, 79 airports), 4,248 FIRMS hotspots.
- **Not ready** (tickets in `PRD.md`):
  - no Dockerfile or deploy (BE-01);
  - Gemini called directly with shut-down model ids and the key in the URL (BE-04);
  - Indonesian strings in engine and impact responses (BE-03b; the API layer and product name are done in BE-03a);
  - no city endpoints, preparedness, alerts or `/chat` yet (BE-05…BE-14).
- **Done on `feat/be-implementation` (2026-10-10):** BE-02 (`.env` loaded, `STANDBAI_OFFLINE` default `0` with legacy fallback, CORS allow-list from `CORS_ORIGINS`) and BE-03a (English API metadata, `data/standbai.db`, English tags `health, events, simulation, analysis, trust, layers, attributions`, `Standbai/1.0` User-Agent).
- **Tests:** 47 passed (`pytest -q`, offline via `tests/conftest.py`; Python 3.13 on the developer machine, and again on Python 3.14 in a clean copy without a local `.env`, 2026-10-10). `ruff check .` reports 139 errors that pre-date BE-02, mostly whitespace in `scripts/`.
  - With a local `.env` whose `CORS_ORIGINS` is a wildcard, `test_cors_rejects_unlisted_origin` fails, because the app loads `.env` during tests. See BE-03a follow-up 3 in `PRD.md`.
- **Open follow-ups** (`PRD.md`, BE-03a):
  - product strings in code still say "Standbai", so rename them to "StandbAI";
  - Indonesian lines left in `app/db`, `app/schemas`, `app/core`;
  - test isolation from `.env`;
  - regenerate `docs/fixtures/` (5 files still carry the old name or Indonesian text);
  - `scripts/github/*` (10 files) automate another project's GitHub board and aren't used by StandbAI: delete or leave (team decision).

- **2026-10-10 21:35 WIB, branch `feat/ai-brief`:** `GET /advice/nearby?lat&lon&lang` (`app/services/advice.py`, tag `analysis`). Facts from our data: volcanoes within 300 km, FIRMS detections within 10/25/50 km, the nearest fire-prone forest, and the closest pass of the 72 h smoke paths (fire clusters) and ash paths (Level III+ volcanoes within 200 km). A fixed rule picks the scenario (`ash_threat`, `smoke_threat`, `prevention`, `clear`). The AI service then writes the brief (`/api/v1/brief`) while its RandomForest scores the 20 nearest detections, in parallel. No LLM key in the backend. 54 tests pass.

## 7. Conventions
- **Times:** UTC ISO 8601.
- **API JSON:** snake_case. New responses carry `generated_at`, `source`, `is_example`.
- **ISPU:** codes `good | moderate | unhealthy | very_unhealthy | hazardous` plus `official_name_id`. Hourly values are labelled "indicative".
- **Constants:** every constant lives in `config/assumptions.yaml` with `status` (`sourced`, `sourced_range`, `sourced_secondary`, `modeling_choice`, `to_verify`, `assumption_placeholder`) and `source`.
- **Secrets:** only in `.env` locally and Cloud Run secrets in production. Never in code, logs, responses or the frontend.
- **Job and alert endpoints** require `X-Job-Token`; AI calls send `X-Internal-Token`.
- **Gates:** `pytest -q` and `ruff check .` before every push.
- **Git:** Conventional Commits in English (`feat(area): add outlook endpoint`); branches `feat/…`, `fix/…`, `docs/…`.

## 8. Decision log
| Date | Decision | Why |
|---|---|---|
| 2026-10-09 | One product name for the platform; English API and docs | International judging |
| 2026-10-09 | Deploy on Google Cloud Run (`asia-southeast2`), 1 instance, CPU always allocated | Background simulations and file-based runs need one warm instance |
| 2026-10-10 | Backend is the single public API (BFF) for web, Telegram/n8n and chat | One contract, one place for keys and validation |
| 2026-10-10 | City-centred endpoints follow the FE prototype's data needs; contracts shared in both PRDs | Lets FE and BE build in parallel |
| 2026-10-10 | Air quality from CAMS via the Open-Meteo Air Quality API (PM2.5, PM10, dust) | Free, no key, forecast + recent past |
| 2026-10-10 | Outlook heuristic v0 today; ML outlook from the AI service when it beats its baseline | Honest and explainable now, better later |
| 2026-10-10 | n8n for scheduled jobs and the Telegram bot; BE stores only `chat_id` + city | Uses a sponsor perk; minimal personal data |
| 2026-10-10 | All LLM calls move behind the AI service (Featherless primary, Gemini fallback) | One gateway, no LLM keys in BE |
| 2026-10-10 | Additive API changes only (`hazard_radius_km` next to `radius_bahaya_km`) | Don't break the existing dashboard on deadline day |
| 2026-10-10 | No Kafka, Spark or MinIO today; scale-up path: GCS, Pub/Sub, BigQuery | Data volume fits SQLite/DuckDB |
| 2026-10-10 | `.env` loaded at startup; `STANDBAI_OFFLINE` defaults to `0`; `UDARASIAGA_OFFLINE` accepted as a legacy fallback for one release | Deployable by default without breaking old scripts |
| 2026-10-10 | CORS allow-list from `CORS_ORIGINS` (no wildcard in production) | Only our web app can call the API from a browser |
| 2026-10-10 | Database file renamed to `data/standbai.db` | Matches the product name |
| 2026-10-10 | English OpenAPI tags (`analysis`, `trust`, …); module files `lapis2.py`, `lapis3.py` keep their names for now | Clear docs without a risky refactor on deadline day |
| 2026-10-10 | Product name spelled **StandbAI** (capital "AI"); lower-case slugs unchanged | Team decision; highlights the AI |

## 9. Links
- Frontend: https://github.com/ITHACKITS/FE-FORGEHACK-2026 · AI: https://github.com/ITHACKITS/AI-FORGEHACK-2026
- Devpost: https://forgehacks-2026.devpost.com
- Live API: *add the Cloud Run URL after BE-01.* · Telegram bot: *add after BE-11.*
