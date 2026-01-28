# Autonomous Software Engineering Team

An autonomous multi-agent system that transforms business ideas into working software.

## Overview

Unlike existing agentic IDEs that require constant human presence and feedback loops, this system operates independently for extended periods—up to a full workday—only surfacing to the user when genuine decisions or clarifications are needed.

The human interacts exclusively with a PM agent via Telegram. The PM triages requests, coordinates the engineering team, and shields the user from implementation noise.

## User Stories

**US-1 — Idea to Implementation**
As a user, I can describe a business idea to the PM via Telegram and receive a working implementation without managing the engineering process.

**US-2 — Minimal Interruptions**
As a user, I only get interrupted when the PM genuinely needs a decision or clarification—not for status updates.

**US-3 — Progress Check-in**
As a user, I can check in on progress anytime by messaging the PM.

**US-4 — Delivery Summary**
As a user, I receive a summary of what was built and how to run it when the work is complete.

## System Stories

- **SS-1** — Task Delegation: The PM agent receives user input, breaks it into tasks, and delegates to specialist agents
- **SS-2** — Async Communication: Agents communicate asynchronously through a shared message bus
- **SS-3** — Task Queue: The system maintains a task queue that agents pull from and update independently
- **SS-4** — Batched Questions: The PM agent aggregates blockers and batches questions to minimize user interruptions
- **SS-5** — Autonomous Testing: The tester agent validates implementations and can trigger rework cycles without human involvement
- **SS-6** — Activity Logging: All agent activity is logged for the PM to summarize on request or at completion

## MVP Scope

- **Agents**: PM, Developer, Tester (architect deferred)
- **Interface**: Telegram bot only
- **Output**: Working code in a git repo + summary message
- **Runtime**: Target 1-8 hours of autonomous work per request

## Repository Structure

```
autonomous-swe-agents/
├── agents/                    # Agent definitions and specifications
│   ├── __init__.py           # Python module init
│   └── rlm_executor.py       # RLM safe execution wrapper
├── tasks/                     # PRDs and progress tracking (Ralph pattern)
│   └── README.md             # Task directory documentation
├── examples/                  # Integration tests and examples
│   └── test_ralph_integration.py
├── tg-webhook/                # Telegram webhook bridge to OpenCode
│   ├── kubernetes/           # Kubernetes manifests
│   ├── webhook.py           # FastAPI webhook server
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Container image
│   └── README.md            # Webhook documentation
├── opencode/                  # OpenCode agent configurations
│   └── .config/agent/        # Agent prompt files (PM, Backend, Frontend, QA)
├── requirements.txt           # Project dependencies (includes RLM)
├── RALPH_RLM_INTEGRATION.md  # Integration documentation
├── QUICK_START.md            # Quick start guide
└── README.md                 # This file
```

## 🚀 New: Ralph + RLM Integration

The system now includes autonomous iteration patterns and safe code execution:

- **Ralph Pattern**: Agents work autonomously through PRDs with quality gates
- **RLM Integration**: Safe, isolated code execution environments
- **Progress Tracking**: Git commits + progress files preserve learnings
- **Quality Enforcement**: Tests/typecheck required before proceeding

See [RALPH_RLM_INTEGRATION.md](RALPH_RLM_INTEGRATION.md) for full details and [QUICK_START.md](QUICK_START.md) for testing instructions.

## Components

### Telegram Webhook

Bridges Telegram Bot API with the OpenCode server. See [tg-webhook/README.md](tg-webhook/README.md) for details.

**Key features:**
- Creates/manages OpenCode sessions per Telegram chat
- Forwards messages to OpenCode API
- Returns AI responses to users via Telegram

## Quick Start

### Telegram Webhook

```bash
cd tg-webhook

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your bot token and OpenCode URL

# Run locally
python webhook.py

# Or deploy to Kubernetes
kubectl apply -f kubernetes/secrets.yaml
kubectl apply -f kubernetes/deployment.yaml
```
