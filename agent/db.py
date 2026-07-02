import json
from datetime import datetime
from pathlib import Path

import aiosqlite

from agent.schema import state_to_dict

DB_PATH = Path("data/sessions.db")


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                status TEXT NOT NULL,
                recommendation TEXT,
                confidence TEXT,
                candidates_found INTEGER,
                decision_log TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        await db.commit()


async def save_session(session_id: str, state) -> None:
    payload = state_to_dict(state)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                state.query.raw_query,
                state.status,
                state.final_recommendation.title if state.final_recommendation else None,
                state.confidence,
                len(state.candidates),
                json.dumps(state.decision_log),
                json.dumps(payload),
                datetime.utcnow().isoformat(),
            ),
        )
        await db.commit()


async def get_recent_sessions(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            """
            SELECT id, query, status, recommendation, confidence, candidates_found, created_at
            FROM sessions ORDER BY created_at DESC LIMIT ?
            """,
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
            keys = [
                "id",
                "query",
                "status",
                "recommendation",
                "confidence",
                "candidates_found",
                "created_at",
            ]
            return [dict(zip(keys, row)) for row in rows]


async def get_session_log(session_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT decision_log FROM sessions WHERE id = ?",
            (session_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return json.loads(row[0]) if row else []


async def get_session_result(session_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT result FROM sessions WHERE id = ?",
            (session_id,),
        ) as cursor:
            row = await cursor.fetchone()
            return json.loads(row[0]) if row else None
