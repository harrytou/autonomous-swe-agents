import os
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
import httpx
from typing import Dict

load_dotenv()

app = FastAPI()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENCODE_URL = os.getenv("OPENCODE_URL", "http://opencode-service:8080")

# Store session IDs per chat_id
chat_sessions: Dict[int, str] = {}


async def send_telegram_message(chat_id: int, text: str):
    """Send a message via Telegram Bot API"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to send Telegram message")
        return response.json()


async def get_or_create_session(chat_id: int) -> str:
    """Get existing session or create a new one for this chat"""
    if chat_id in chat_sessions:
        return chat_sessions[chat_id]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OPENCODE_URL}/session",
                json={"title": f"Telegram Chat {chat_id}"}
            )

            if response.status_code in [200, 201]:
                session_data = response.json()
                session_id = session_data.get("id")
                chat_sessions[chat_id] = session_id
                print(f"[Session] Created new session {session_id} for chat_id={chat_id}")
                return session_id
            else:
                raise Exception(f"Failed to create session: {response.status_code}")

    except Exception as e:
        raise Exception(f"Error creating session: {str(e)}")


async def send_message_to_opencode(session_id: str, user_message: str) -> str:
    """Send message to OpenCode session and get response"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OPENCODE_URL}/session/{session_id}/message",
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
        return "Request is being processed. This may take a while - I'll get back to you when it's done."
    except Exception as e:
        return f"Error communicating with OpenCode server: {str(e)}"


@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram webhook updates"""
    try:
        data = await request.json()

        # Extract message info
        if "message" not in data:
            return {"status": "ok"}

        message = data["message"]
        chat_id = message["chat"]["id"]

        # Handle text messages only
        if "text" not in message:
            await send_telegram_message(chat_id, "Please send a text message.")
            return {"status": "ok"}

        user_message = message["text"]

        # Log incoming message
        print(f"[Telegram] Received message from chat_id={chat_id}: {user_message}")

        # Skip bot commands for now
        if user_message.startswith("/"):
            if user_message == "/start":
                await send_telegram_message(
                    chat_id,
                    "👋 Welcome! I'm your PM agent. Describe your business idea and I'll help you build it."
                )
            return {"status": "ok"}

        # Send "typing" action
        async with httpx.AsyncClient() as http_client:
            await http_client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendChatAction",
                json={"chat_id": chat_id, "action": "typing"}
            )

        # Get or create session for this chat
        try:
            session_id = await get_or_create_session(chat_id)
        except Exception as e:
            await send_telegram_message(chat_id, f"Failed to initialize session: {str(e)}")
            return {"status": "error", "message": str(e)}

        # Send message to OpenCode server
        response = await send_message_to_opencode(session_id, user_message)

        # Log response
        print(f"[OpenCode] Response for chat_id={chat_id}: {response}")

        # Send response back to user
        await send_telegram_message(chat_id, response)

        return {"status": "ok"}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
