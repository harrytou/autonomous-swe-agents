# Telegram Webhook for OpenCode

A simple FastAPI webhook that bridges Telegram Bot API with the OpenCode server.

## How It Works

1. User sends a message to the Telegram bot
2. Webhook receives the message via POST `/webhook`
3. Creates or retrieves an OpenCode session for that chat
4. Forwards the message to OpenCode using `POST /session/:id/message`
5. Extracts the response from OpenCode
6. Sends the response back to the user via Telegram

## Session Management

- Each Telegram chat gets its own OpenCode session
- Sessions are created on first interaction and reused for subsequent messages
- Session IDs are stored in memory (will reset on pod restart)

## API Integration

### OpenCode Endpoints Used

- `POST /session` - Create a new session with title "Telegram Chat {chat_id}"
- `POST /session/:id/message` - Send message with parts array containing text

### Telegram Bot API

- `POST /webhook` - Receives incoming messages
- Sends responses via `sendMessage` API
- Shows typing indicator while processing

## Configuration

Set these environment variables:

- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `OPENCODE_URL` - OpenCode server URL (default: `http://opencode-service:8080`)

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your bot token

# Run
python webhook.py

# Set webhook URL
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_URL>/webhook"
```

## Kubernetes Deployment

```bash
# Update secrets
kubectl apply -f kubernetes/secrets.yaml

# Deploy
kubectl apply -f kubernetes/deployment.yaml
```

## Health Check

`GET /health` returns `{"status": "healthy"}`
