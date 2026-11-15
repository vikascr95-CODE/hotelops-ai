# HotelOps AI

A hotel operations backend with an AI layer. Staff manage rooms, guests, bookings and service requests. An ML triage agent sorts incoming requests, and a document-based knowledge base answers policy questions only from the hotel's own documents.

![Dashboard](docs/dashboard.png)

## What it does

- **Booking engine.** Prevents double bookings (a stay ending on the 12th and one starting on the 12th are allowed), calculates the total price, checks availability across dates, and enforces a fixed status path: `confirmed → checked_in → checked_out`. Checking in and out also updates the room's status.
- **AI triage agent.** Reads a service request ("the air conditioner is not working") and suggests a category, priority and the team that should handle it. Two scikit-learn text classifiers do the prediction, with safety rules on top (see below).
- **Knowledge base.** Upload a PDF or TXT file, and ask questions in plain English. Answers come from ranked passages (BM25) with the source document shown. If nothing matches, it says so and does not invent an answer.
- **Authentication.** Registration and login with hashed passwords and token-based sessions.
- **Dashboard.** A single page at `/dashboard/` showing live counts, the request queue with one-click AI triage, and the knowledge base.

## Safety design for the agent

1. **Emergencies never depend on the model.** Words like fire, smoke, gas, flooding or medical trouble force the category `safety` and priority `urgent`.
2. **Low confidence goes to a human.** If the model is unsure, the request is flagged for review and nothing is changed automatically.
3. **The agent can raise a priority, never lower it.** A priority set by a person is never reduced.
4. **Closed requests are never touched.**

## Architecture

```mermaid
flowchart LR
    UI[Dashboard] --> API[FastAPI]
    API --> Booking[Booking engine]
    API --> Triage[Triage agent<br/>scikit-learn + safety rules]
    API --> KB[Knowledge base<br/>chunking + BM25]
    Booking --> DB[(PostgreSQL)]
    Triage --> DB
    KB --> DB
```

## Tech stack

Python, FastAPI, SQLAlchemy 2, PostgreSQL, Alembic migrations, Pydantic v2, scikit-learn, pypdf, pytest.

## Run it locally

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/hotelops_db
```

```bash
alembic upgrade head
uvicorn main:app --reload
```

- API docs: http://127.0.0.1:8000/docs
- Dashboard: http://127.0.0.1:8000/dashboard/
- Demo data (optional): `python scripts/seed_demo.py`

## Tests

```bash
pytest -v
```

76 automated tests cover bookings (overlaps, back-to-back stays, pricing, status rules), guests, rooms, service requests, authentication, uploads, knowledge search, and the triage agent. The tests run against a temporary in-memory database and never touch real data.

## Honest limits

- The triage classifiers learn from a small hand-written dataset (about 60 examples). They get 8 out of 8 unseen test phrases right, which is a useful baseline and not a benchmark. More data would improve them.
- Knowledge search uses keyword ranking (BM25), not embeddings. Swapping in vector search is a planned upgrade.
- Scanned PDFs without a text layer are rejected (they would need OCR).

## Roadmap

Login on all management endpoints, an LLM step for low-confidence requests, vector search, and a guest-facing chat.
