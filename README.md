# Shopping Agent

Spec-based AI shopping agent demo with a Python FastAPI backend, LangGraph orchestration, Playwright browsing, Claude tool calling, SQLite decision logging, and a Next.js frontend.

## What It Demonstrates

- LangGraph multi-step orchestration: planner -> searcher -> extractor -> reviewer -> comparator -> synthesizer
- Autonomous browser control via headless Playwright
- Typed structured extraction and review through Claude tool calling
- Full decision log observability in SQLite
- Hard autonomy boundary: the agent recommends products but never purchases or checks out

## Project Structure

```text
agent/                 FastAPI + LangGraph backend
  nodes/               Agent graph nodes
  tools/               Playwright and Claude tool schemas
  main.py              API entry point
  graph.py             LangGraph workflow
  schema.py            Pydantic contracts
  db.py                SQLite persistence
frontend/              Next.js frontend
data/                  SQLite database directory
tests/                 Backend unit tests
```

## Backend Setup

```bash
cd agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
set ANTHROPIC_API_KEY=your_key_here
uvicorn agent.main:app --reload --app-dir ..
```

Backend endpoints:

- `GET /health`
- `POST /search` with `{ "query": "wireless earbuds under $100 with good bass" }`
- `GET /sessions`
- `GET /sessions/{session_id}/log`
- `GET /status/{session_id}`

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` if the backend is not on `http://localhost:8000`.

## Autonomy Boundary

The agent has no checkout, cart, payment, or purchase tool. Playwright is only used for search pages and product page text extraction. The final node returns a recommendation and stops.

## Known Constraints

- BestBuy and Walmart are the intended demo targets. Amazon is intentionally excluded because it blocks automated browsing aggressively.
- Live retail pages change frequently, so selectors may need maintenance.
- Extraction confidence is surfaced instead of hidden when pages are sparse or noisy.
