# Database module
from .database import init_db, get_db
from .users import (
    User,
    get_user_by_telegram_id,
    create_user,
    get_or_create_user,
    update_user_activity,
    set_user_whitelist,
)
from .sessions import (
    Session,
    get_session_by_opencode_id,
    get_active_session_for_user,
    get_sessions_for_user,
    create_session,
    update_session_activity,
    update_session_title,
    deactivate_session,
    deactivate_all_user_sessions,
)
from .projects import (
    Project,
    get_project_by_id,
    get_project_by_name,
    get_projects_for_user,
    create_project,
    update_project,
    delete_project,
)

__all__ = [
    # Database
    "init_db",
    "get_db",
    # Users
    "User",
    "get_user_by_telegram_id",
    "create_user",
    "get_or_create_user",
    "update_user_activity",
    "set_user_whitelist",
    # Sessions
    "Session",
    "get_session_by_opencode_id",
    "get_active_session_for_user",
    "get_sessions_for_user",
    "create_session",
    "update_session_activity",
    "update_session_title",
    "deactivate_session",
    "deactivate_all_user_sessions",
    # Projects
    "Project",
    "get_project_by_id",
    "get_project_by_name",
    "get_projects_for_user",
    "create_project",
    "update_project",
    "delete_project",
]
