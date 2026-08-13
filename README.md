\# TaskFlow



An internal task and project management platform: FastAPI backend, vanilla

JS/HTML/CSS dashboard, custom sorting/search algorithms, and an AI Quick Add

feature with a deterministic parser plus optional Groq LLM enhancement.



\## Features



\- Users, Projects, Tasks — full CRUD, backed by SQLAlchemy models

\- Project statistics via SQL `COUNT()` / `GROUP BY` aggregation

\- Custom \*\*insertion sort\*\* for `GET /tasks?sort=priority` (no `sorted()`)

\- Custom \*\*binary search\*\* and \*\*linear search\*\* for `GET /tasks/search`

\- AI Quick Add: type a sentence, get a structured task

&#x20; - Deterministic mock parser (always available, no API key required)

&#x20; - Optional Groq LLM parser (OpenAI-compatible API), with automatic

&#x20;   fallback to the mock parser on any failure

\- Request logging middleware (method, path, ms)

\- Responsive single-page dashboard, localStorage cache, no `innerHTML`

&#x20; for user data

\- Single FastAPI process serves both the API and the frontend (no CORS

&#x20; headaches in production)

\- Ready for Render: `/health` endpoint, `$PORT` binding, `DATABASE\_URL`

&#x20; switch between SQLite (local) and PostgreSQL (production)



\## Tech Stack



\*\*Backend:\*\* Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.x, Pydantic v2,

python-dotenv, OpenAI SDK (Groq-compatible)

\*\*Frontend:\*\* HTML5, CSS3, vanilla JavaScript (no frameworks)

\*\*Database:\*\* SQLite (local) / PostgreSQL (production, via `DATABASE\_URL`)

\*\*Deployment:\*\* Render Web Service



\## Architecture



```

Browser (dashboard)

&#x20;     |

&#x20;     | fetch() -> relative paths (/tasks, /projects, /users)

&#x20;     v

FastAPI app (backend/main.py)

&#x20;     |-- RequestLoggingMiddleware

&#x20;     |-- CORS

&#x20;     |-- routers: users, projects, tasks

&#x20;     |-- static frontend mounted at /static, index served at /

&#x20;     v

SQLAlchemy ORM (backend/models.py)

&#x20;     v

SQLite (local) or PostgreSQL (DATABASE\_URL set)

```



\## Folder Structure



```

taskflow/

├── backend/

│   ├── main.py            FastAPI app, CORS, middleware, static mount

│   ├── database.py        Engine/session, get\_db()

│   ├── models.py          User, Project, Task ORM models

│   ├── schemas.py         Pydantic v2 request/response schemas

│   ├── dependencies.py    Re-exports get\_db

│   ├── middleware.py      Request logging

│   ├── algorithms.py      insertion\_sort, binary\_search, linear\_search (+ \*\_count)

│   ├── ai\_parser.py       Deterministic mock parser (mandatory path)

│   ├── groq\_service.py    Optional Groq LLM parser + fallback logic

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

├── check\_algorithms.py

├── benchmark\_algorithms.py

├── requirements.txt

├── .env.example

├── .gitignore

├── render.yaml

└── README.md

```



\## Database Schema



\*\*users\*\*: `id (PK)`, `name`, `email (UNIQUE, NOT NULL)`

\*\*projects\*\*: `id (PK)`, `name (NOT NULL)`, `owner\_id (FK -> users.id, NOT NULL)`

\*\*tasks\*\*: `id (PK)`, `title (NOT NULL)`, `priority (NOT NULL: low|medium|high)`, `due\_date (TEXT, nullable)`, `project\_id (FK -> projects.id, NOT NULL)`



Relationships: `User 1--N Project`, `Project 1--N Task`, both directions

navigable via SQLAlchemy `relationship(back\_populates=...)`.



\## Environment Setup



\*\*Windows (PowerShell):\*\*

```powershell

python -m venv venv

venv\\Scripts\\Activate.ps1

pip install -r requirements.txt

copy .env.example .env

```



\*\*macOS / Linux:\*\*

```bash

python -m venv venv

source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

```



\## Running the App Locally



```bash

\# optional: seed some demo data

python -m backend.seed



\# start the server

uvicorn backend.main:app --reload

```



\- Dashboard: `http://127.0.0.1:8000/` (served directly by FastAPI)

\- Interactive API docs (Swagger UI): `http://127.0.0.1:8000/docs`



\### Environment Variables



| Variable | Purpose | Default |

|---|---|---|

| `DATABASE\_URL` | Postgres URL in production; unset = local SQLite | unset |

| `GROQ\_API\_KEY` | Groq API key, server-side only | unset |

| `GROQ\_MODEL` | Groq model name | `llama-3.1-8b-instant` |

| `USE\_REAL\_LLM` | `true` to attempt Groq before falling back to mock | `false` |

| `FRONTEND\_URL` | Extra allowed CORS origin in production | unset |

| `PORT` | Server port (set automatically by Render) | `8000` |



\### Running checks and benchmarks



```bash

python check\_algorithms.py

python benchmark\_algorithms.py

```



\## API Documentation



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

| GET | `/tasks?project\_id=\&sort=priority` | List tasks, optional custom sort | 200 | - |

| GET | `/tasks/search?title=\&algo=binary\\|linear` | Search by exact title | 200 | 404 |

| POST | `/tasks/quick-add` | AI-parsed task creation | 201 | 422 |

| GET | `/tasks/{id}` | Get one task | 200 | 404 |

| PUT | `/tasks/{id}` | Update a task | 200 | 404, 422 |

| DELETE | `/tasks/{id}` | Delete a task | 200 | 404 |

| GET | `/health` | Health check | 200 | - |



\### Worked examples per endpoint category



\*\*Create\*\* — `POST /tasks`



Request body:

```json

{ "title": "Write API docs", "priority": "medium", "due\_date": "next friday", "project\_id": 1 }

```

Response `201`:

```json

{ "id": 4, "title": "Write API docs", "priority": "medium", "due\_date": "next friday", "project\_id": 1 }

```



\*\*List\*\* — `GET /tasks?project\_id=1`



Response `200`:

```json

\[

&#x20; { "id": 1, "title": "Design database schema", "priority": "high", "due\_date": "tomorrow", "project\_id": 1 },

&#x20; { "id": 4, "title": "Write API docs", "priority": "medium", "due\_date": "next friday", "project\_id": 1 }

]

```



\*\*Get by id\*\* — `GET /tasks/4`



Response `200`:

```json

{ "id": 4, "title": "Write API docs", "priority": "medium", "due\_date": "next friday", "project\_id": 1 }

```

Response `404` (unknown id):

```json

{ "detail": "Task not found" }

```



\*\*Update\*\* — `PUT /tasks/4`



Request body:

```json

{ "priority": "high" }

```

Response `200`:

```json

{ "id": 4, "title": "Write API docs", "priority": "high", "due\_date": "next friday", "project\_id": 1 }

```



\*\*Delete\*\* — `DELETE /tasks/4`



Response `200`:

```json

{ "message": "Task deleted successfully" }

```



\*\*Statistics\*\* — `GET /projects/statistics`



Response `200`:

```json

\[

&#x20; { "project\_id": 1, "project\_name": "Inventory API", "task\_count": 3, "low\_count": 1, "medium\_count": 1, "high\_count": 1 }

]

```



\*\*Sorted list (custom insertion sort)\*\* — `GET /tasks?project\_id=1\&sort=priority`



Response `200` (ascending by priority weight low=1, medium=2, high=3):

```json

\[

&#x20; { "id": 3, "title": "Refactor auth module", "priority": "low", "due\_date": "next friday", "project\_id": 1 },

&#x20; { "id": 4, "title": "Write API docs", "priority": "medium", "due\_date": "next friday", "project\_id": 1 },

&#x20; { "id": 1, "title": "Design database schema", "priority": "high", "due\_date": "tomorrow", "project\_id": 1 }

]

```



\*\*Search (custom binary/linear search)\*\* — `GET /tasks/search?title=Write%20API%20docs\&algo=binary`



Response `200`:

```json

{ "id": 4, "title": "Write API docs", "priority": "high", "due\_date": "next friday", "project\_id": 1 }

```

Response `404` (no exact title match):

```json

{ "detail": "Task not found" }

```



\*\*Quick add (AI parser)\*\* — `POST /tasks/quick-add`



Request body:

```json

{ "description": "Finish the report tomorrow urgent", "project\_id": 1 }

```

Response `201`:

```json

{ "id": 5, "title": "Finish the report", "priority": "high", "due\_date": "tomorrow", "project\_id": 1 }

```



\## AI Quick Add



\### Deterministic mock parser (mandatory, default)



Priority keywords checked in order: `urgent`/`asap` → high;

`whenever`/`low priority` → low; otherwise → medium. If both a high and

low signal are present, high wins. All matched keyword phrases and the

matched due-date phrase are stripped from the original-case description

to build the title; an empty result becomes `"Untitled task"`.



Date phrases checked in order: `today`, `tomorrow`, `next week`,

`next monday`..`next sunday`, then `monday`..`sunday`. First match wins.



\### Optional Real LLM



The real Groq LLM integration is optional and is controlled by the

`USE\_REAL\_LLM` feature flag. The default configuration keeps this flag

disabled, so the AI quick-add feature works without an API key or

network access. When enabled, the Groq model is used for

natural-language task parsing, while the application retains a

deterministic fallback parser if the LLM request fails.



Set `USE\_REAL\_LLM=true` and `GROQ\_API\_KEY` to route through Groq's

OpenAI-compatible chat completions endpoint. The response is parsed as

JSON and validated with the same `ParsedTask` Pydantic model used by the

mock parser. Any JSON error, validation error, or network error falls

back to the mock parser automatically — the endpoint never crashes and

never requires Groq to function.



\### Five worked examples



| Input | Parsed JSON |

|---|---|

| `"Finish the report tomorrow urgent"` | `{"title":"Finish the report","priority":"high","due\_date\_hint":"tomorrow"}` |

| `"Call the vendor ASAP"` | `{"title":"Call the vendor","priority":"high","due\_date\_hint":null}` |

| `"Reorganize the archive, low priority, whenever"` | `{"title":"Reorganize the archive","priority":"low","due\_date\_hint":null}` |

| `"Review the design next friday"` | `{"title":"Review the design","priority":"medium","due\_date\_hint":"next friday"}` |

| `"Water the office plants"` | `{"title":"Water the office plants","priority":"medium","due\_date\_hint":null}` |



\### Prompting technique (≤300 words)



This is a \*\*zero-shot, schema-constrained\*\* prompt: a single system

message states the task, the output format (JSON only), and the exact

field set (`title`, `priority`, `due\_date\_hint`), with priority

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



\## Render Deployment



1\. Push this repository to GitHub.

2\. In Render, create a new \*\*Web Service\*\* from the repo (or use the

&#x20;  included `render.yaml` via "New +" → "Blueprint").

3\. Build command: `pip install -r requirements.txt`

4\. Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

5\. Set environment variables in the Render dashboard: `DATABASE\_URL`

&#x20;  (if using Render Postgres), `GROQ\_API\_KEY`, `GROQ\_MODEL`,

&#x20;  `USE\_REAL\_LLM`, `FRONTEND\_URL`, `PYTHON\_VERSION`.

6\. Render will health-check `/health`.



Because the frontend is served by FastAPI itself at `/`, there is

nothing else to deploy separately — one Web Service is the whole app.



\## Git Workflow



```

main

&#x20; |

&#x20; |---- feature/readme-documentation

&#x20;         |-- commit 1: document environment setup and app running

&#x20;         |-- commit 2: document optional real LLM and fallback behavior

&#x20;         |

&#x20;         merge into main

main

```



\## Algorithm Complexity



| Algorithm | Time | Space |

|---|---|---|

| Insertion sort | O(n²) worst/avg, O(n) best (nearly sorted) | O(1) extra |

| Binary search | O(log n) | O(1) |

| Linear search | O(n) | O(1) |



Run `python benchmark\_algorithms.py` to generate comparison counts at

10 / 500 / 3000 records; results are printed and saved to

`benchmark\_results.txt`.



\*\*Sample benchmark results:\*\*



```

n=   10 | insertion\_sort comparisons=      22 | binary\_search comparisons=   3 | linear\_search comparisons=     7

n=  500 | insertion\_sort comparisons=   39999 | binary\_search comparisons=   1 | linear\_search comparisons=   352

n= 3000 | insertion\_sort comparisons= 1493234 | binary\_search comparisons=  11 | linear\_search comparisons=  2686

```



\## Troubleshooting



\- \*\*`ModuleNotFoundError: backend`\*\* — run commands from the project

&#x20; root (`taskflow/`), not from inside `backend/`.

\- \*\*CORS errors locally\*\* — serve the frontend from

&#x20; `http://localhost:5500` (e.g. VS Code Live Server) or just use the

&#x20; FastAPI-served copy at `http://127.0.0.1:8000/`.

\- \*\*Groq errors\*\* — check `USE\_REAL\_LLM` and `GROQ\_API\_KEY`; the app

&#x20; will keep working via the mock parser regardless.

\- \*\*SQLite locked / data missing on Render\*\* — Render's local disk is

&#x20; ephemeral; set `DATABASE\_URL` to a managed PostgreSQL instance for

&#x20; production persistence.

\- \*\*Build fails on Render with a Rust/cargo error\*\* — pin the Python

&#x20; version via `runtime.txt` (`python-3.12.7`) so pre-built wheels are

&#x20; used instead of building `pydantic-core` from source.



