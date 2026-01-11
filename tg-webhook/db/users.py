from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from .database import get_db


@dataclass
class User:
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_whitelisted: bool
    created_at: datetime
    last_active_at: datetime


async def get_user_by_telegram_id(telegram_id: int) -> Optional[User]:
    """Get user by Telegram ID."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?",
            (telegram_id,)
        )
        row = await cursor.fetchone()
        if row:
            return User(
                id=row["id"],
                telegram_id=row["telegram_id"],
                username=row["username"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                is_whitelisted=bool(row["is_whitelisted"]),
                created_at=row["created_at"],
                last_active_at=row["last_active_at"]
            )
        return None


async def create_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    is_whitelisted: bool = False
) -> User:
    """Create a new user."""
    async with get_db() as db:
        cursor = await db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name, last_name, is_whitelisted)
            VALUES (?, ?, ?, ?, ?)
            """,
            (telegram_id, username, first_name, last_name, is_whitelisted)
        )
        await db.commit()
        user_id = cursor.lastrowid

        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = await cursor.fetchone()
        return User(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            is_whitelisted=bool(row["is_whitelisted"]),
            created_at=row["created_at"],
            last_active_at=row["last_active_at"]
        )


async def get_or_create_user(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
) -> User:
    """Get existing user or create a new one."""
    user = await get_user_by_telegram_id(telegram_id)
    if user:
        # Update last active and user info
        await update_user_activity(telegram_id, username, first_name, last_name)
        return await get_user_by_telegram_id(telegram_id)
    return await create_user(telegram_id, username, first_name, last_name)


async def update_user_activity(
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
) -> None:
    """Update user's last active timestamp and info."""
    async with get_db() as db:
        await db.execute(
            """
            UPDATE users
            SET last_active_at = CURRENT_TIMESTAMP,
                username = COALESCE(?, username),
                first_name = COALESCE(?, first_name),
                last_name = COALESCE(?, last_name)
            WHERE telegram_id = ?
            """,
            (username, first_name, last_name, telegram_id)
        )
        await db.commit()


async def set_user_whitelist(telegram_id: int, is_whitelisted: bool) -> bool:
    """Set user whitelist status. Returns True if user exists."""
    async with get_db() as db:
        cursor = await db.execute(
            "UPDATE users SET is_whitelisted = ? WHERE telegram_id = ?",
            (is_whitelisted, telegram_id)
        )
        await db.commit()
        return cursor.rowcount > 0
