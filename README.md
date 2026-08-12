# TaskFlow

An internal task and project management platform: FastAPI backend, vanilla
JS/HTML/CSS dashboard, custom sorting/search algorithms, and an AI Quick Add
feature with a deterministic parser plus optional Groq LLM enhancement.

## Features

- Users, Projects, Tasks — full CRUD, backed by SQLAlchemy models
- Project statistics via SQL `COUNT()` / `GROUP BY` aggregation
- Custom **insertion sort** for `GET /tasks?sort=priority` (no `sorted()`)
- Custom **binary search** and **linear search** for `GET /tasks/search`
- AI Quick Add: type a sentence, get a structured task
  - Deterministic mock parser (always available, no API key required)
  - Optional Groq LLM parser (OpenAI-compatible API), with automatic
    fallback to the mock parser on any failure
- Request logging middleware (method, path, ms)
- Responsive single-page dashboard, localStorage cache, no `innerHTML`
  for user data
- Single FastAPI process serves both the API and the frontend (no CORS
  headaches in production)
- Ready for Render: `/health` endpoint, `$PORT` binding, `DATABASE_URL`
  switch between SQLite (local) and PostgreSQL (production)

## Tech Stack

**Backend:** Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic v2,
python-dotenv, OpenAI SDK (Groq-compatible)
**Frontend:** HTML5, CSS3, vanilla JavaScript (no frameworks)
**Database:** SQLite (local) / PostgreSQL (production, via `DATABASE_URL`)
**Deployment:** Render Web Service

## Architecture

```
Browser (dashboard)
      |
      | fetch() -> relative paths (/tasks, /projects, /users)
      v
FastAPI app (backend/main.py)
      |-- RequestLoggingMiddleware
      |-- CORS
      |-- routers: users, projects, tasks
      |-- static frontend mounted at /static, index served at /
      v
SQLAlchemy ORM (backend/models.py)
      v
SQLite (local) or PostgreSQL (DATABASE_URL set)
```

## Folder Structure

```
taskflow/
├── backend/
│   ├── main.py            FastAPI app, CORS, middleware, static mount
│   ├── database.py        Engine/session, get_db()
│   ├── models.py          User, Project, Task ORM models
│   ├── schemas.py         Pydantic v2 request/response schemas
│   ├── dependencies.py    Re-exports get_db
│   ├── middleware.py      Request logging
│   ├── algorithms.py      insertion_sort, binary_search, linear_search (+ *_count)
│   ├── ai_parser.py       Deterministic mock parser (mandatory path)
│   ├── groq_service.py    Optional Groq LLM parser + fallback logic
│   ├── crud.py            DB access functions
│   ├── seed.py            Optional demo data seeder
│   └── routes/
│       ├── users.py
│       ├── projects.py
│       └── tasks.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── check_algorithms.py
├── benchmark_algorithms.py
├── requirements.txt
├── .env.example
├── .gitignore
├── render.yaml
└── README.md
```

## Database Schema

**users**: `id (PK)`, `name`, `email (UNIQUE, NOT NULL)`
**projects**: `id (PK)`, `name (NOT NULL)`, `owner_id (FK -> users.id, NOT NULL)`
**tasks**: `id (PK)`, `title (NOT NULL)`, `priority (NOT NULL: low|medium|high)`, `due_date (TEXT, nullable)`, `project_id (FK -> projects.id, NOT NULL)`

Relationships: `User 1--N Project`, `Project 1--N Task`, both directions
navigable via SQLAlchemy `relationship(back_populates=...)`.

## API Documentation

Interactive docs available at `/docs` once running (FastAPI's built-in
Swagger UI).

| Method | Path | Description | Success | Errors |
|---|---|---|---|---|
| POST | `/users` | Create a user | 201 | 422 |
| GET | `/users` | List users | 200 | - |
| POST | `/projects` | Create a project | 201 | 422 |
| GET | `/projects` | List projects | 200 | - |
| GET | `/projects/statistics` | Per-project task counts (SQL aggregated) | 200 | - |
| POST | `/tasks` | Create a task | 201 | 422 |
| GET | `/tasks?project_id=&sort=priority` | List tasks, optional custom sort | 200 | - |
| GET | `/tasks/search?title=&algo=binary\|linear` | Search by exact title | 200 | 404 |
| POST | `/tasks/quick-add` | AI-parsed task creation | 201 | 422 |
| GET | `/tasks/{id}` | Get one task | 200 | 404 |
| PUT | `/tasks/{id}` | Update a task | 200 | 404, 422 |
| DELETE | `/tasks/{id}` | Delete a task | 200 | 404 |
| GET | `/health` | Health check | 200 | - |

**Example — create task**

Request: `POST /tasks`
```json
{ "title": "Write API docs", "priority": "medium", "due_date": "next friday", "project_id": 1 }
```
Response `201`:
```json
{ "id": 4, "title": "Write API docs", "priority": "medium", "due_date": "next friday", "project_id": 1 }
```

**Example — statistics**

`GET /projects/statistics` → `200`
```json
[{ "project_id": 1, "project_name": "Inventory API", "task_count": 3, "low_count": 1, "medium_count": 1, "high_count": 1 }]
```

## Local Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # edit if needed

# optional demo data
python -m backend.seed

uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/` — the dashboard is served directly by
FastAPI. API docs at `http://127.0.0.1:8000/docs`.

### Environment Variables

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | Postgres URL in production; unset = local SQLite | unset |
| `GROQ_API_KEY` | Groq API key, server-side only | unset |
| `GROQ_MODEL` | Groq model name | `llama-3.1-8b-instant` |
| `USE_REAL_LLM` | `true` to attempt Groq before falling back to mock | `false` |
| `FRONTEND_URL` | Extra allowed CORS origin in production | unset |
| `PORT` | Server port (set automatically by Render) | `8000` |

### Running checks and benchmarks

```bash
python check_algorithms.py
python benchmark_algorithms.py
```

## AI Quick Add

### Deterministic mock parser (mandatory, default)

Priority keywords checked in order: `urgent`/`asap` → high;
`whenever`/`low priority` → low; otherwise → medium. If both a high and
low signal are present, high wins. All matched keyword phrases and the
matched due-date phrase are stripped from the original-case description
to build the title; an empty result becomes `"Untitled task"`.

Date phrases checked in order: `today`, `tomorrow`, `next week`,
`next monday`..`next sunday`, then `monday`..`sunday`. First match wins.

### Five worked examples

| Input | Parsed JSON |
|---|---|
| `"Finish the report tomorrow urgent"` | `{"title":"Finish the report","priority":"high","due_date_hint":"tomorrow"}` |
| `"Call the vendor ASAP"` | `{"title":"Call the vendor","priority":"high","due_date_hint":null}` |
| `"Reorganize the archive, low priority, whenever"` | `{"title":"Reorganize the archive","priority":"low","due_date_hint":null}` |
| `"Review the design next friday"` | `{"title":"Review the design","priority":"medium","due_date_hint":"next friday"}` |
| `"Water the office plants"` | `{"title":"Water the office plants","priority":"medium","due_date_hint":null}` |

### Groq path (optional)

Set `USE_REAL_LLM=true` and `GROQ_API_KEY` to route through Groq's
OpenAI-compatible chat completions endpoint. The response is parsed as
JSON and validated with the same `ParsedTask` Pydantic model used by the
mock parser. Any JSON error, validation error, or network error falls
back to the mock parser automatically — the endpoint never crashes and
never requires Groq to function.

### Prompting technique (≤300 words)

This is a **zero-shot, schema-constrained** prompt: a single system
message states the task, the output format (JSON only), and the exact
field set (`title`, `priority`, `due_date_hint`), with priority
restricted to an enum. No worked examples are included in the prompt
itself — few-shot examples would add meaningfully to token usage on
every request for a marginal accuracy gain on a task this narrow, and
the deterministic mock parser already handles the well-defined keyword
patterns the capstone requires. Chain-of-thought is deliberately
excluded: asking the model to reason step-by-step before answering
would both increase token usage and risk the model wrapping its
reasoning around the JSON, breaking strict parsing. `temperature=0` is
used to keep output as deterministic as an LLM can be.

Reliability comes from defense in depth, not from the prompt alone: the
raw response is JSON-parsed defensively (stripping markdown fences),
then validated against the same Pydantic schema used elsewhere in the
app, and any failure at any stage — network, JSON, or validation —
falls back to the deterministic parser rather than surfacing an error
to the user. This makes Groq a pure enhancement: when it works, results
can capture nuance the keyword parser misses; when it doesn't, the user
never notices, because task creation still succeeds.

This approach was chosen because Quick Add is a narrow, structured
extraction task (three fields, one of them an enum) — exactly the kind
of task where a tightly-constrained zero-shot prompt is more reliable
and cheaper than a longer few-shot or chain-of-thought prompt would be.

## Render Deployment

1. Push this repository to GitHub.
2. In Render, create a new **Web Service** from the repo (or use the
   included `render.yaml` via "New +" → "Blueprint").
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Set environment variables in the Render dashboard: `DATABASE_URL`
   (if using Render Postgres), `GROQ_API_KEY`, `GROQ_MODEL`,
   `USE_REAL_LLM`, `FRONTEND_URL`.
6. Render will health-check `/health`.

Because the frontend is served by FastAPI itself at `/`, there is
nothing else to deploy separately — one Web Service is the whole app.

## Git Workflow

```
main
  |
  |---- feature/taskflow-core
          |-- commit 1: backend (models, schemas, crud, routes, algorithms)
          |-- commit 2: frontend (dashboard, styles, script) + README
          |
          merge --no-ff into main
main
```

## Algorithm Complexity

| Algorithm | Time | Space |
|---|---|---|
| Insertion sort | O(n²) worst/avg, O(n) best (nearly sorted) | O(1) extra |
| Binary search | O(log n) | O(1) |
| Linear search | O(n) | O(1) |

Run `python benchmark_algorithms.py` to generate comparison counts at
10 / 500 / 3000 records; results are printed and saved to
`benchmark_results.txt`.

## Troubleshooting

- **`ModuleNotFoundError: backend`** — run commands from the project
  root (`taskflow/`), not from inside `backend/`.
- **CORS errors locally** — serve the frontend from
  `http://localhost:5500` (e.g. VS Code Live Server) or just use the
  FastAPI-served copy at `http://127.0.0.1:8000/`.
- **Groq errors** — check `USE_REAL_LLM` and `GROQ_API_KEY`; the app
  will keep working via the mock parser regardless.
- **SQLite locked / data missing on Render** — Render's local disk is
  ephemeral; set `DATABASE_URL` to a managed PostgreSQL instance for
  production persistence.
