import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import httpx
from typing import Optional

from config import config
from db import (
    init_db,
    get_or_create_user,
    get_user_by_telegram_id,
    get_active_session_for_user,
    get_sessions_for_user,
    create_session as db_create_session,
    update_session_activity,
    deactivate_all_user_sessions,
    get_projects_for_user,
    get_project_by_name,
    create_project as db_create_project,
    User,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


async def send_telegram_message(chat_id: int, text: str, parse_mode: str = "Markdown"):
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"

    # Truncate long messages (Telegram limit is 4096)
    if len(text) > 4000:
        text = text[:4000] + "\n\n... (message truncated)"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            # Try without parse mode if markdown fails
            payload["parse_mode"] = None
            response = await client.post(url, json=payload)
        return response.json()


async def send_typing_action(chat_id: int):
    """Send typing indicator."""
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendChatAction"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "action": "typing"})


def is_user_allowed(user: User) -> bool:
    """Check if user is allowed to use the bot."""
    if config.ALLOW_ALL_USERS:
        return True
    if user.is_whitelisted:
        return True
    if user.telegram_id in config.WHITELIST_USER_IDS:
        return True
    return False


async def create_opencode_session(directory: Optional[str] = None, title: Optional[str] = None) -> str:
    """Create a new OpenCode session and return session ID."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {}
            if directory:
                payload["directory"] = directory
            if title:
                payload["title"] = title

            response = await client.post(
                f"{config.OPENCODE_URL}/session",
                json=payload,
                headers={"x-opencode-directory": directory} if directory else {}
            )

            if response.status_code in [200, 201]:
                session_data = response.json()
                return session_data.get("id")
            else:
                raise Exception(f"Failed to create session: {response.status_code} - {response.text}")

    except Exception as e:
        raise Exception(f"Error creating OpenCode session: {str(e)}")


async def get_or_create_opencode_session(user: User, project_id: Optional[int] = None, directory: Optional[str] = None) -> tuple:
    """Get existing session or create a new one. Returns (session_id, db_session)."""
    # Check for existing active session
    db_session = await get_active_session_for_user(user.id, project_id)

    if db_session:
        return db_session.opencode_session_id, db_session

    # Create new OpenCode session
    title = f"Telegram - {user.username or user.first_name or user.telegram_id}"
    opencode_session_id = await create_opencode_session(directory=directory, title=title)

    # Save to database
    db_session = await db_create_session(
        user_id=user.id,
        opencode_session_id=opencode_session_id,
        title=title,
        project_id=project_id
    )

    print(f"[Session] Created new session {opencode_session_id} for user {user.telegram_id}")
    return opencode_session_id, db_session


async def send_message_to_opencode(session_id: str, user_message: str) -> str:
    """Send message to OpenCode session and get response."""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{config.OPENCODE_URL}/session/{session_id}/message",
                json={
                    "parts": [
                        {
                            "type": "text",
                            "text": user_message
                        }
                    ]
                }
            )

            if response.status_code == 200:
                data = response.json()
                # Extract text from response parts
                if isinstance(data, dict) and "parts" in data:
                    parts = data["parts"]
                    text_parts = [p.get("text", "") for p in parts if p.get("type") == "text"]
                    return "\n".join(text_parts) if text_parts else "Request processed."
                elif isinstance(data, list):
                    # Handle array of message objects
                    text_parts = []
                    for msg in data:
                        if "parts" in msg:
                            text_parts.extend([p.get("text", "") for p in msg["parts"] if p.get("type") == "text"])
                    return "\n".join(text_parts) if text_parts else "Request processed."
                else:
                    return "Request processed successfully."
            else:
                return f"Error: OpenCode server returned status {response.status_code}"

    except httpx.TimeoutException:
        return "Request is being processed. This may take a while..."
    except Exception as e:
        return f"Error communicating with OpenCode server: {str(e)}"


# Command handlers

async def cmd_start(chat_id: int, user: User):
    """Handle /start command."""
    welcome = (
        "Welcome! I'm your AI coding assistant.\n\n"
        "Commands:\n"
        "/newproject <name> - Create a new project\n"
        "/projects - List your projects\n"
        "/sessions - List your sessions\n"
        "/newsession - Start a fresh session\n"
        "/help - Show this message\n\n"
        "Just send me a message to start chatting!"
    )
    await send_telegram_message(chat_id, welcome)


async def cmd_help(chat_id: int, user: User):
    """Handle /help command."""
    help_text = (
        "*Available Commands:*\n\n"
        "/newproject <name> - Create a new project with git repo\n"
        "/projects - List all your projects\n"
        "/sessions - List your recent sessions\n"
        "/newsession - Start a fresh conversation\n"
        "/project <name> - Switch to a project context\n"
        "/help - Show this message\n\n"
        "Send any message to interact with the AI agent."
    )
    await send_telegram_message(chat_id, help_text)


async def cmd_sessions(chat_id: int, user: User):
    """Handle /sessions command."""
    sessions = await get_sessions_for_user(user.id, limit=10)

    if not sessions:
        await send_telegram_message(chat_id, "You don't have any sessions yet. Start chatting to create one!")
        return

    lines = ["*Your Recent Sessions:*\n"]
    for i, session in enumerate(sessions, 1):
        status = "Active" if session.is_active else "Ended"
        title = session.title or "Untitled"
        lines.append(f"{i}. {title} ({status})")

    await send_telegram_message(chat_id, "\n".join(lines))


async def cmd_newsession(chat_id: int, user: User):
    """Handle /newsession command."""
    # Deactivate all existing sessions
    await deactivate_all_user_sessions(user.id)
    await send_telegram_message(chat_id, "Started a new session. Your previous sessions are still saved.")


async def cmd_projects(chat_id: int, user: User):
    """Handle /projects command."""
    projects = await get_projects_for_user(user.id)

    if not projects:
        await send_telegram_message(
            chat_id,
            "You don't have any projects yet.\n\nUse /newproject <name> to create one!"
        )
        return

    lines = ["*Your Projects:*\n"]
    for project in projects:
        desc = f" - {project.description}" if project.description else ""
        lines.append(f"- *{project.name}*{desc}")

    lines.append("\n_Use /project <name> to work on a project_")
    await send_telegram_message(chat_id, "\n".join(lines))


async def cmd_newproject(chat_id: int, user: User, args: str):
    """Handle /newproject command."""
    if not args.strip():
        await send_telegram_message(
            chat_id,
            "Please provide a project name.\n\nUsage: /newproject my-awesome-app"
        )
        return

    # Parse name and optional description
    parts = args.strip().split(" ", 1)
    name = parts[0]
    description = parts[1] if len(parts) > 1 else None

    # Check if project exists
    existing = await get_project_by_name(user.id, name)
    if existing:
        await send_telegram_message(
            chat_id,
            f"Project '{name}' already exists. Choose a different name."
        )
        return

    try:
        await send_typing_action(chat_id)
        project = await db_create_project(user.id, name, description)

        await send_telegram_message(
            chat_id,
            f"Project *{name}* created!\n\n"
            f"Path: `{project.path}`\n"
            f"Git repo initialized with initial commit.\n\n"
            f"Use /project {name} to start working on it."
        )

    except Exception as e:
        await send_telegram_message(chat_id, f"Failed to create project: {str(e)}")


async def cmd_project(chat_id: int, user: User, args: str):
    """Handle /project command - switch to project context."""
    if not args.strip():
        await send_telegram_message(
            chat_id,
            "Please specify a project name.\n\nUsage: /project my-app"
        )
        return

    name = args.strip()
    project = await get_project_by_name(user.id, name)

    if not project:
        await send_telegram_message(
            chat_id,
            f"Project '{name}' not found.\n\nUse /projects to see your projects."
        )
        return

    # Deactivate current sessions and create new one for this project
    await deactivate_all_user_sessions(user.id)

    try:
        await send_typing_action(chat_id)
        session_id, _ = await get_or_create_opencode_session(
            user,
            project_id=project.id,
            directory=project.path
        )

        await send_telegram_message(
            chat_id,
            f"Switched to project *{name}*.\n\n"
            f"Working directory: `{project.path}`\n\n"
            f"Send me a message to start working on this project!"
        )

    except Exception as e:
        await send_telegram_message(chat_id, f"Failed to switch project: {str(e)}")


# Command router
COMMANDS = {
    "/start": (cmd_start, False),
    "/help": (cmd_help, False),
    "/sessions": (cmd_sessions, False),
    "/newsession": (cmd_newsession, False),
    "/projects": (cmd_projects, False),
    "/newproject": (cmd_newproject, True),  # requires args
    "/project": (cmd_project, True),  # requires args
}


async def handle_command(chat_id: int, user: User, text: str) -> bool:
    """Handle bot commands. Returns True if handled."""
    parts = text.split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""

    if cmd in COMMANDS:
        handler, needs_args = COMMANDS[cmd]
        if needs_args:
            await handler(chat_id, user, args)
        else:
            await handler(chat_id, user)
        return True

    return False


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram webhook updates."""
    try:
        data = await request.json()

        # Extract message info
        if "message" not in data:
            return {"status": "ok"}

        message = data["message"]
        chat_id = message["chat"]["id"]
        from_user = message.get("from", {})

        # Get or create user
        user = await get_or_create_user(
            telegram_id=from_user.get("id", chat_id),
            username=from_user.get("username"),
            first_name=from_user.get("first_name"),
            last_name=from_user.get("last_name")
        )

        # Check if user is allowed
        if not is_user_allowed(user):
            await send_telegram_message(
                chat_id,
                "Sorry, you're not authorized to use this bot. Contact the administrator."
            )
            return {"status": "ok"}

        # Handle text messages only
        if "text" not in message:
            await send_telegram_message(chat_id, "Please send a text message.")
            return {"status": "ok"}

        user_message = message["text"]
        print(f"[Telegram] Received from {user.username or user.telegram_id}: {user_message[:100]}")

        # Handle commands
        if user_message.startswith("/"):
            handled = await handle_command(chat_id, user, user_message)
            if handled:
                return {"status": "ok"}
            # Unknown command
            await send_telegram_message(chat_id, "Unknown command. Use /help to see available commands.")
            return {"status": "ok"}

        # Send typing indicator
        await send_typing_action(chat_id)

        # Get or create session
        try:
            session_id, db_session = await get_or_create_opencode_session(user)
        except Exception as e:
            await send_telegram_message(chat_id, f"Failed to initialize session: {str(e)}")
            return {"status": "error", "message": str(e)}

        # Update session activity
        await update_session_activity(db_session.id)

        # Send message to OpenCode server
        response = await send_message_to_opencode(session_id, user_message)
        print(f"[OpenCode] Response for {user.telegram_id}: {response[:100]}...")

        # Send response back to user
        await send_telegram_message(chat_id, response)

        return {"status": "ok"}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
