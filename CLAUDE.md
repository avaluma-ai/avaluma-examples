# CLAUDE.md

Public examples that show customers how to integrate Avaluma avatars. Overview and
architecture: [README.md](README.md).

- [avatar-server/](avatar-server/README.md): run the Avaluma Avatar Server
  (`ghcr.io/avaluma-ai/avaluma-avatar-server`) with Docker, optionally behind Caddy.
- [livekit-agent/](livekit-agent/README.md): two LiveKit agents that drive an avatar through
  `avaluma-livekit-plugin`.

This repository is **public**. Never commit license keys, API keys, internal hostnames or
internal paths; `.env*` files stay local. Write for customers: every example must work with
only the README and the customer's own credentials.

## Build

entfällt – the examples are built by the customer. `livekit-agent/Dockerfile` builds the agent
image during `docker compose up`.

## Test

No test suite. After a change, check the files that changed:

```bash
docker compose -f avatar-server/docker-compose.yaml config -q
docker compose -f avatar-server/reverse_proxy/docker-compose.yaml config -q
python3 -m py_compile livekit-agent/agents/*/*.py
```

`docker compose config` for `livekit-agent/` needs a `.env.local` there (copy `.env.example`).

## Deploy

entfällt – merging to `main` publishes the change, customers clone the repository.

## Verify

Follow the changed README from a fresh clone, with a test license key and a LiveKit project:
the avatar server starts, the agent joins the room, and the avatar answers.
