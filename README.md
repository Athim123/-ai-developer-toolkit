# AI Developer Toolkit

A working MVP implementation of the design in `docs/architecture.md` (Section 8 API design,
Section 9 database design), covering prompt management, workflow orchestration, tool
execution, evaluation, and lightweight retrieval — powered by **Groq** as the LLM provider.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set GROQ_API_KEY=gsk_...

uvicorn app.main:app --reload
```

The API is now at `http://localhost:8000`, with interactive docs at `http://localhost:8000/docs`.
SQLite (`toolkit.db`) is used by default — swap `DATABASE_URL` in `.env` for a Postgres URL
to match the production design (Section 4.2/9.1); models are written with SQLAlchemy so
this requires no code changes.

## Auth flow

```bash
# 1. Register
curl -X POST localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"You","password":"pass1234"}'

# 2. Login (OAuth2 password flow -> JWT)
curl -X POST localhost:8000/v1/auth/login \
  -F "username=you@example.com" -F "password=pass1234"
# -> {"access_token": "...", "token_type": "bearer"}

# 3. Create a project (send the token as a Bearer header on every call below)
curl -X POST localhost:8000/v1/projects \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Project"}'
```

## Run a workflow (Section 8.1, POST /v1/runs)

```bash
curl -X POST localhost:8000/v1/runs \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
        "project_id": "proj_xxx",
        "workflow": "code_assist",
        "input": {"task": "What is 42 * 17? Use the calculator tool."},
        "tools": ["calculator"]
      }'
```

Response includes `run_id`, `status`, and `trace_url` — fetch `GET /v1/runs/{run_id}/trace`
for the full step-by-step trace (model calls, tool calls, latency).

## Other endpoints

| Endpoint | Purpose |
|---|---|
| `POST /v1/prompts` | Create/version a prompt template |
| `GET /v1/prompts/{id}` | Fetch a prompt version |
| `GET /v1/tools` | List available tools |
| `POST /v1/tools/execute` | Directly invoke a tool |
| `POST /v1/evaluate` | LLM-as-judge scoring of a completed run |
| `POST /v1/retrieval/documents` | Index a document for a project |
| `POST /v1/retrieval/query` | Semantic search over indexed documents |

## Notes on this implementation vs. the full design doc

- **LLM provider**: Groq (`groq` Python SDK) instead of a generic OpenAI-compatible client.
  Default model is `llama-3.3-70b-versatile` — override per-request via `model`, or globally
  via `GROQ_MODEL` in `.env`.
- **Retrieval**: uses a dependency-free hashed bag-of-words + cosine similarity instead of a
  hosted embeddings API, since Groq doesn't currently serve embeddings. Swap
  `app/retrieval/rag_service.py` for a real embedding model and a pgvector column when you
  move off SQLite — the API surface (`/v1/retrieval/*`) won't need to change.
- **Async workers / Celery / Redis** (Section 4.2, 5.6) are not included — runs execute
  synchronously in the request. This matches the "Day 3: MVP API shell with one workflow run
  endpoint" milestone; queueing is the natural next step for long-running workflows.
- **Observability stack** (OpenTelemetry/Prometheus/Grafana) is represented here by the
  `TraceEvent` table + `GET /v1/runs/{id}/trace`; wiring real OTel exporters is straightforward
  from `app/workflows/engine.py`.

## Tests

```bash
pip install pytest
pytest tests/unit
```
