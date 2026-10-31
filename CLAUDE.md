# CLAUDE.md

Public examples that show customers how to integrate Avaluma avatars. Overview and
architecture: [README.md](README.md).

- [avatar-server/](avatar-server/README.md): run the Avaluma Avatar Server
  (`ghcr.io/avaluma-ai/avaluma-avatar-server`) with Docker, optionally behind Caddy.
- [livekit-agent/](livekit-agent/README.md): two LiveKit agents that drive an avatar through
  `livekit-plugins-avaluma` (module `livekit.plugins.avaluma`), pinned to a commit of
  [avaluma-livekit-plugin](https://github.com/avaluma-ai/avaluma-livekit-plugin) in
  `livekit-agent/pyproject.toml`; exact versions in `livekit-agent/uv.lock`.

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

Import test: installs the locked dependencies and imports both agents without starting them, so a
renamed package or module fails here (`py_compile` does not notice):

```bash
(cd livekit-agent && uv sync --locked && for f in agents/*/agent-*.py; do
  PYTHONPATH="$(dirname "$f")" uv run python -c "import runpy, sys; runpy.run_path(sys.argv[1])" "$f" || exit 1
done)
```

After changing `livekit-agent/pyproject.toml`, run `uv lock` there and commit `uv.lock`;
`uv sync --locked` (also in the Dockerfile) fails on a stale lock.

`docker compose config` for `livekit-agent/` needs a `.env.local` there (copy `.env.example`).

## Deploy

entfällt – merging to `main` publishes the change, customers clone the repository.

## Verify

Follow the changed README from a fresh clone, with a test license key and a LiveKit project:
the avatar server starts, the agent joins the room, and the avatar answers.
