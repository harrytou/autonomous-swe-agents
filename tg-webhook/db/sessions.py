from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from .database import get_db


@dataclass
class Session:
    id: int
    user_id: int
    project_id: Optional[int]
    opencode_session_id: str
    title: Optional[str]
    is_active: bool
    created_at: datetime
    last_message_at: datetime


async def get_session_by_opencode_id(opencode_session_id: str) -> Optional[Session]:
    """Get session by OpenCode session ID."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM sessions WHERE opencode_session_id = ?",
            (opencode_session_id,)
        )
        row = await cursor.fetchone()
        if row:
            return Session(
                id=row["id"],
                user_id=row["user_id"],
                project_id=row["project_id"],
                opencode_session_id=row["opencode_session_id"],
                title=row["title"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_message_at=row["last_message_at"]
            )
        return None


async def get_active_session_for_user(user_id: int, project_id: Optional[int] = None) -> Optional[Session]:
    """Get the active session for a user, optionally for a specific project."""
    async with get_db() as db:
        if project_id is not None:
            cursor = await db.execute(
                """
                SELECT * FROM sessions
                WHERE user_id = ? AND project_id = ? AND is_active = TRUE
                ORDER BY last_message_at DESC LIMIT 1
                """,
                (user_id, project_id)
            )
        else:
            cursor = await db.execute(
                """
                SELECT * FROM sessions
                WHERE user_id = ? AND project_id IS NULL AND is_active = TRUE
                ORDER BY last_message_at DESC LIMIT 1
                """,
                (user_id,)
            )
        row = await cursor.fetchone()
        if row:
            return Session(
                id=row["id"],
                user_id=row["user_id"],
                project_id=row["project_id"],
                opencode_session_id=row["opencode_session_id"],
                title=row["title"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_message_at=row["last_message_at"]
            )
        return None


async def get_sessions_for_user(user_id: int, limit: int = 10) -> List[Session]:
    """Get all sessions for a user, ordered by most recent."""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT * FROM sessions
            WHERE user_id = ?
            ORDER BY last_message_at DESC
            LIMIT ?
            """,
            (user_id, limit)
        )
        rows = await cursor.fetchall()
        return [
            Session(
                id=row["id"],
                user_id=row["user_id"],
                project_id=row["project_id"],
                opencode_session_id=row["opencode_session_id"],
                title=row["title"],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_message_at=row["last_message_at"]
            )
            for row in rows
        ]


async def create_session(
    user_id: int,
    opencode_session_id: str,
    title: Optional[str] = None,
    project_id: Optional[int] = None
) -> Session:
    """Create a new session."""
    async with get_db() as db:
        cursor = await db.execute(
            """
            INSERT INTO sessions (user_id, project_id, opencode_session_id, title)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, project_id, opencode_session_id, title)
        )
        await db.commit()
        session_id = cursor.lastrowid

        cursor = await db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = await cursor.fetchone()
        return Session(
            id=row["id"],
            user_id=row["user_id"],
            project_id=row["project_id"],
            opencode_session_id=row["opencode_session_id"],
            title=row["title"],
            is_active=bool(row["is_active"]),
            created_at=row["created_at"],
            last_message_at=row["last_message_at"]
        )


async def update_session_activity(session_id: int) -> None:
    """Update session's last message timestamp."""
    async with get_db() as db:
        await db.execute(
            "UPDATE sessions SET last_message_at = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,)
        )
        await db.commit()


async def update_session_title(session_id: int, title: str) -> None:
    """Update session title."""
    async with get_db() as db:
        await db.execute(
            "UPDATE sessions SET title = ? WHERE id = ?",
            (title, session_id)
        )
        await db.commit()


async def deactivate_session(session_id: int) -> None:
    """Mark a session as inactive."""
    async with get_db() as db:
        await db.execute(
            "UPDATE sessions SET is_active = FALSE WHERE id = ?",
            (session_id,)
        )
        await db.commit()


async def deactivate_all_user_sessions(user_id: int) -> None:
    """Deactivate all sessions for a user."""
    async with get_db() as db:
        await db.execute(
            "UPDATE sessions SET is_active = FALSE WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()
