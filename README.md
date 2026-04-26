# Avaluma Examples

A collection of examples showing how to integrate **Avaluma AI Avatars** into your applications.

## Examples

| Example | Description |
|---|---|
| [`avatar-server`](./avatar-server/) | Deploy the Avaluma Avatar Server with Docker and an optional Caddy reverse proxy. Supports multiple simultaneous avatar sessions with GPU acceleration. |
| [`livekit-agent`](./livekit-agent/) | LiveKit Agents that drive an Avaluma avatar. Includes a full voice AI pipeline (STT → LLM → TTS) and an example of streaming audio directly to the avatar from an external source via DataStream. |

## Architecture Overview

The **LiveKit Agent** handles the conversational AI pipeline (STT → LLM → TTS) and sends audio to the **Avatar Server**, which animates a photorealistic avatar and streams the video back into the LiveKit room.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- An [Avaluma](https://avaluma.ai) license key and `.hvia` avatar file(s)
- A [LiveKit](https://livekit.io) account (Cloud or self-hosted)
- NVIDIA GPU (required by the avatar server)

## Getting Started

1. Start with the [`avatar-server`](./avatar-server/) to host your avatars.
2. Then set up the [`livekit-agent`](./livekit-agent/) to connect it to a LiveKit room.
