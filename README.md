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
├── agents/          # Agent definitions and specifications
├── kubernetes/      # Kubernetes manifests for deployment
└── README.md        # This file
```

## Getting Started

_Coming soon_
