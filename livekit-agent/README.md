# LiveKit Agent

A [LiveKit Agent](https://docs.livekit.io/agents/) that drives an Avaluma avatar with a full voice AI pipeline. When a user joins a LiveKit room, the agent processes their speech, generates a response, and animates the avatar to deliver it.

## Pipeline

```
Microphone → STT → LLM → TTS → Avaluma Avatar → Video stream
             │                         │
       AssemblyAI              Avatar Server
       (universal-           (animates .hvia
        streaming)              avatar file)
               LLM: OpenAI GPT-4.1-mini
               TTS: Cartesia Sonic-3
```

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- A running [avatar-server](../avatar-server/) instance
- A [LiveKit](https://livekit.io) account (Cloud or self-hosted)
- An Avaluma license key

## Setup

### 1. Configure Environment Variables

Copy `.env.example` to `.env.local` and fill in your credentials:

```bash
cp .env.example .env.local
```

```env
AVALUMA_LICENSE_KEY=""     # Your Avaluma license key
AVATAR_SERVER_URL="https://your-avatar-server.com" # Avaluma Hosted https://api.avaluma.ai

LIVEKIT_URL=""             # wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=""         # API key from your LiveKit project
LIVEKIT_API_SECRET=""      # API secret from your LiveKit project
```

### 2. Configure the Agent

Edit `agents/agent-1.py` to set your avatar:

```python
avatar_id = "your-avatar-id"          # Must match the .hvia filename (without extension)
```

### 3. Start the Agent

```bash
docker compose up -d
```

The agent will connect to LiveKit and wait for users to join a room.

## Adding More Agents

To run multiple agents (e.g., for different rooms or avatars), add another service to `docker-compose.yaml`:

```yaml
services:
  livekit-agent-2:
    build: .
    env_file:
      - .env.local
    environment:
      - AGENT_NAME=agent-2
    volumes:
      - livekit_plugin_cache:/root/.cache
      - ./agents/agent-2.py:/app/src/agent.py
    network_mode: host
```

Then create the corresponding `agents/agent-2.py` file. Each agent must have a unique `AGENT_NAME`.

## Configuration

| Variable | Description |
|---|---|
| `AVALUMA_LICENSE_KEY` | Your Avaluma license key |
| `LIVEKIT_URL` | WebSocket URL of your LiveKit server |
| `LIVEKIT_API_KEY` | LiveKit project API key |
| `LIVEKIT_API_SECRET` | LiveKit project API secret |
| `AVATAR_SERVER_URL` | URL of the running avatar server (default: `https://api.avaluma.ai`) |
| `AGENT_NAME` | Unique name for this agent worker (default: `agent-1`) |

## Dependencies

Managed by [uv](https://github.com/astral-sh/uv) via `pyproject.toml`:

| Package | Purpose |
|---|---|
| `livekit-agents` | Core agent framework |
| `livekit-plugins-noise-cancellation` | Background noise suppression (BVC) |
| `avaluma-livekit-plugin` | Avaluma avatar integration |
| `silero` | Voice activity detection (VAD) |
| `turn-detector` | Multilingual end-of-turn detection |
