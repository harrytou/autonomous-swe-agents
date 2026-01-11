import os
import subprocess
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime
from .database import get_db

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


@dataclass
class Project:
    id: int
    user_id: int
    name: str
    description: Optional[str]
    path: str
    created_at: datetime
    updated_at: datetime


async def get_project_by_id(project_id: int) -> Optional[Project]:
    """Get project by ID."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM projects WHERE id = ?",
            (project_id,)
        )
        row = await cursor.fetchone()
        if row:
            return Project(
                id=row["id"],
                user_id=row["user_id"],
                name=row["name"],
                description=row["description"],
                path=row["path"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        return None


async def get_project_by_name(user_id: int, name: str) -> Optional[Project]:
    """Get project by user and name."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT * FROM projects WHERE user_id = ? AND name = ?",
            (user_id, name)
        )
        row = await cursor.fetchone()
        if row:
            return Project(
                id=row["id"],
                user_id=row["user_id"],
                name=row["name"],
                description=row["description"],
                path=row["path"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        return None


async def get_projects_for_user(user_id: int) -> List[Project]:
    """Get all projects for a user."""
    async with get_db() as db:
        cursor = await db.execute(
            """
            SELECT * FROM projects
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [
            Project(
                id=row["id"],
                user_id=row["user_id"],
                name=row["name"],
                description=row["description"],
                path=row["path"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            for row in rows
        ]


def create_project_directory(user_id: int, project_name: str) -> str:
    """Create project directory and initialize git repo. Returns the path."""
    # Sanitize project name for filesystem
    safe_name = "".join(c for c in project_name if c.isalnum() or c in "-_").lower()
    if not safe_name:
        safe_name = "project"

    # Create path: /data/projects/{user_id}/{project_name}
    project_path = os.path.join(config.PROJECTS_DIR, str(user_id), safe_name)

    # Handle duplicate names by appending number
    base_path = project_path
    counter = 1
    while os.path.exists(project_path):
        project_path = f"{base_path}-{counter}"
        counter += 1

    # Create directory
    os.makedirs(project_path, exist_ok=True)

    # Initialize git repo
    subprocess.run(
        ["git", "init"],
        cwd=project_path,
        capture_output=True,
        check=True
    )

    # Create initial README
    readme_path = os.path.join(project_path, "README.md")
    with open(readme_path, "w") as f:
        f.write(f"# {project_name}\n\nProject created via Telegram bot.\n")

    # Initial commit
    subprocess.run(
        ["git", "add", "."],
        cwd=project_path,
        capture_output=True,
        check=True
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=project_path,
        capture_output=True,
        check=True
    )

    return project_path


async def create_project(
    user_id: int,
    name: str,
    description: Optional[str] = None
) -> Project:
    """Create a new project with git repo."""
    # Create directory and git repo
    project_path = create_project_directory(user_id, name)

    async with get_db() as db:
        cursor = await db.execute(
            """
            INSERT INTO projects (user_id, name, description, path)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, name, description, project_path)
        )
        await db.commit()
        project_id = cursor.lastrowid

        cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = await cursor.fetchone()
        return Project(
            id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            description=row["description"],
            path=row["path"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )


async def update_project(
    project_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> None:
    """Update project details."""
    async with get_db() as db:
        if name is not None:
            await db.execute(
                "UPDATE projects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (name, project_id)
            )
        if description is not None:
            await db.execute(
                "UPDATE projects SET description = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (description, project_id)
            )
        await db.commit()


async def delete_project(project_id: int) -> bool:
    """Delete a project from database (does not delete files). Returns True if deleted."""
    async with get_db() as db:
        cursor = await db.execute(
            "DELETE FROM projects WHERE id = ?",
            (project_id,)
        )
        await db.commit()
        return cursor.rowcount > 0
