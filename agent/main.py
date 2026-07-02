import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.db import get_recent_sessions, get_session_log, get_session_result, init_db, save_session
from agent.graph import run_agent
from agent.schema import AgentState, SearchQuery, state_to_dict

load_dotenv()

app = FastAPI(title="Shopping Agent")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchPayload(BaseModel):
    query: str


@app.on_event("startup")
async def startup() -> None:
    await init_db()


@app.post("/search")
async def search(payload: SearchPayload):
    session_id = str(uuid.uuid4())
    state = AgentState(query=SearchQuery(raw_query=payload.query))
    result = await run_agent(state)
    await save_session(session_id, result)
    return {"session_id": session_id, **state_to_dict(result)}


@app.get("/sessions")
async def sessions():
    return await get_recent_sessions()


@app.get("/sessions/{session_id}/log")
async def session_log(session_id: str):
    return await get_session_log(session_id)


@app.get("/status/{session_id}")
async def status(session_id: str):
    result = await get_session_result(session_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "status": result["status"],
        "error": result.get("error"),
        "decision_log": result.get("decision_log", []),
    }


@app.get("/health")
def health():
    return {"status": "ok"}
