# Telegram Webhook for OpenCode

A FastAPI webhook service that bridges Telegram Bot API with OpenCode, featuring persistent session management, user access control, and project creation with git repositories.

## Features

- **User Management**: Automatic user creation with whitelist-based access control
- **Session Persistence**: SQLite-backed session storage (survives pod restarts)
- **Project Management**: Create projects with initialized git repos
- **Multi-user Support**: Each user gets their own sessions and projects

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message with command list |
| `/help` | Show available commands |
| `/newproject <name> [description]` | Create a new project with git repo |
| `/projects` | List your projects |
| `/project <name>` | Switch to a project context |
| `/sessions` | List your recent sessions |
| `/newsession` | Start a fresh conversation |

## How It Works

1. User sends a message to the Telegram bot
2. Webhook authenticates user against whitelist
3. Creates or retrieves user from SQLite database
4. Gets or creates an OpenCode session for that user
5. Forwards the message to OpenCode
6. Sends the response back to the user

## Data Persistence

All data is stored in `/data` (mounted as PVC in Kubernetes):

```
/data
├── db/
│   └── swe-agents.db    # SQLite database
└── projects/
    └── {user_id}/
        └── {project_name}/  # Git repositories
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Required |
| `OPENCODE_URL` | OpenCode server URL | `http://opencode-server:4000` |
| `DATA_DIR` | Data directory path | `/data` |
| `ALLOW_ALL_USERS` | Allow any user | `false` |
| `WHITELIST_USER_IDS` | Comma-separated user IDs | Empty |

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your bot token and whitelist

# Run
python webhook.py

# Set webhook URL (use ngrok for local testing)
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook?url=<YOUR_URL>/webhook"
```

## Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace swe-agents

# Apply PVC (uses local-path storage class for Raspberry Pi)
kubectl apply -f kubernetes/pvc.yaml

# Update secrets with your values
kubectl apply -f kubernetes/secrets.yaml

# Deploy
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

### Storage Class

The PVC uses `local-path` storage class, which is the default provisioner for k3s/Rancher on Raspberry Pi clusters.

## Database Schema

### Users
- `telegram_id`: Unique Telegram user ID
- `username`, `first_name`, `last_name`: User info
- `is_whitelisted`: Manual whitelist flag
- Timestamps: `created_at`, `last_active_at`

### Sessions
- `user_id`: Foreign key to users
- `project_id`: Optional foreign key to projects
- `opencode_session_id`: OpenCode session reference
- `title`: Session title
- `is_active`: Whether session is current
- Timestamps: `created_at`, `last_message_at`

### Projects
- `user_id`: Foreign key to users
- `name`: Project name (unique per user)
- `description`: Optional description
- `path`: Filesystem path to git repo
- Timestamps: `created_at`, `updated_at`

## Health Check

`GET /health` returns `{"status": "healthy"}`
