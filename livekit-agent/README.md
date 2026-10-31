# LiveKit Agent

A [LiveKit Agent](https://docs.livekit.io/agents/) that drives an Avaluma avatar. Two example agents are included, each demonstrating a different approach to sending audio to the avatar.

## Agents

| Agent | Description |
|---|---|
| [`agent-1`](./agents/1-agent-with-livekit-inference/) | Full voice AI pipeline: STT → LLM → TTS via LiveKit Inference. The standard conversational agent. |
| [`agent-2`](./agents/2-agent-with-external-audio/) | Sends audio directly to the avatar via LiveKit DataStream, bypassing the AgentSession pipeline. Demonstrates how an external service can stream audio to the avatar independently. |

## Pipeline

**agent-1** — conversational voice AI:
```
Microphone → STT → LLM → TTS → Avaluma Avatar → Video stream
             │                         │
       AssemblyAI              Avatar Server
       (universal-           (animates .hvia
        streaming)              avatar file)
               LLM: OpenAI GPT-4.1-mini
               TTS: Cartesia Sonic-3
```

**agent-2** — external audio source:
```
WAV file ──→ DataStream ──→ Avaluma Avatar → Video stream
(external sender,                   │
 own LiveKit token)          Avatar Server
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
AVATAR_SERVER_URL="https://your-avatar-server.com" # Avaluma Hosted: https://api.avaluma.ai

LIVEKIT_URL=""             # wss://your-livekit-instance.livekit.cloud
LIVEKIT_API_KEY=""         # API key from your LiveKit project
LIVEKIT_API_SECRET=""      # API secret from your LiveKit project
```

Without explicit arguments the plugin falls back to `AVALUMA_API_KEY` and `AVALUMA_API_URL`; these examples read `AVALUMA_LICENSE_KEY` and `AVATAR_SERVER_URL` and pass them to `AvatarSession` explicitly.

### 2. Configure the Avatar ID

Set your avatar ID in the agent file. The value must match the `.hvia` filename without the extension.

**agent-1:** `agents/1-agent-with-livekit-inference/agent-1.py`
**agent-2:** `agents/2-agent-with-external-audio/agent-2.py`

```python
avatar_id = "your-avatar-id"
```

### 3. Start the Agents

```bash
docker compose up -d
```

Both agents start by default. To run only one:

```bash
docker compose up livekit-agent-1 -d
```

## Docker Compose

Both agents are pre-configured in `docker-compose.yaml`. agent-2 mounts additional files for its external sender module and audio assets:

```yaml
livekit-agent-2:
  build: .
  env_file:
    - .env.local
  volumes:
    - livekit_plugin_cache:/root/.cache
    - ./agents/2-agent-with-external-audio/agent-2.py:/app/src/agent.py
    - ./agents/2-agent-with-external-audio/external_audio_sender.py:/app/src/external_audio_sender.py
    - ./agents/2-agent-with-external-audio/assets:/app/src/assets
```

## Testing

Once all services are running (avatar server, LiveKit server, and the agent), you can connect to the agent using one of two clients:

| Client | When to use |
|---|---|
| **[Avaluma Test Client](https://avaluma.ai/test-client)** | Works with any LiveKit setup — self-hosted or cloud. |
| **[LiveKit Agent Playground](https://agents-playground.livekit.io)** | Available when using a LiveKit Cloud project. |

### LiveKit Agent Playground

1. Open the [LiveKit Agent Playground](https://agents-playground.livekit.io)
2. Select your LiveKit Cloud project or enter your server credentials
3. Enter the agent name, i.e. the `agent_name` variable in the agent script (e.g. `agent-1`)
4. Click **Connect**

> If the agent doesn't respond after changing the agent name, reload the page and reconnect.

## Adding a New Agent

1. Create a directory under `agents/` with your agent script.
2. Add a service to `docker-compose.yaml`, mounting the script to `/app/src/agent.py`.
3. Set a unique `agent_name` variable inside the script; clients dispatch the agent by this name.

## Configuration

| Variable | Description |
|---|---|
| `AVALUMA_LICENSE_KEY` | Your Avaluma license key |
| `LIVEKIT_URL` | WebSocket URL of your LiveKit server |
| `LIVEKIT_API_KEY` | LiveKit project API key |
| `LIVEKIT_API_SECRET` | LiveKit project API secret |
| `AVATAR_SERVER_URL` | URL of the running avatar server (default: `https://api.avaluma.ai`) |

## Dependencies

Managed by [uv](https://github.com/astral-sh/uv) via `pyproject.toml`. `uv.lock` pins the exact versions, and the Docker build installs them with `uv sync --locked`. After changing `pyproject.toml`, run `uv lock` to update `uv.lock`:

| Package | Purpose |
|---|---|
| `livekit` | LiveKit RTC SDK (room, track, DataStream) |
| `livekit-agents` | Core agent framework, incl. LiveKit Inference, turn detector and Silero VAD |
| `livekit-plugins-noise-cancellation` | Background noise suppression (BVC) |
| `livekit-plugins-avaluma` | Avaluma avatar integration (`livekit.plugins.avaluma`) |
| `python-dotenv` | Loads `.env.local` credentials |
