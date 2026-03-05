# Avatar Server

Hosts the Avaluma Avatar Server using Docker. It renders photorealistic AI avatars and streams the result into a LiveKit room. Multiple avatar sessions with different avatars can run simultaneously.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- NVIDIA GPU with drivers installed
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- An Avaluma license key and at least one `.hvia` avatar file

## Directory Structure

```
avatar-server/
├── assets/
│   └── avatars/          # Place your .hvia avatar files here
├── reverse_proxy/        # Optional: Caddy HTTPS reverse proxy
│   ├── Caddyfile
│   └── docker-compose.yaml
└── docker-compose.yaml
```

## Setup

### 1. Add Avatar Files

Place your `.hvia` avatar files in the `assets/avatars/` directory:

```
assets/avatars/
└── your-avatar-id.hvia
```

### 2. Configure the Environment

Open `docker-compose.yaml` and set the API utility password:

```yaml
environment:
  - API_UTILS_PWD="your-secure-password"
```

### 3. Start the Server

```bash
docker compose up -d
```

The server will be available at `http://localhost:8080`.

## Optional: HTTPS Reverse Proxy

For production deployments, use the included Caddy reverse proxy to terminate TLS automatically.

### 1. Update the Domain

Edit `reverse_proxy/Caddyfile` and replace `api.avaluma.ai` with your own domain:

```
your.domain.com {
    reverse_proxy avaluma-avatar-server:8080
    ...
}
```

### 2. Start the Proxy

Make sure the avatar server is already running (both compose files share the `avaluma-net` network), then start the proxy:

```bash
cd reverse_proxy
docker compose up -d
```

Caddy will automatically obtain and renew a TLS certificate for your domain.

## Configuration

| Variable | Description |
|---|---|
| `API_UTILS_PWD` | Password for the avatar server utility API |

## Notes

- The server requires an NVIDIA GPU. The `deploy.resources` block in `docker-compose.yaml` configures GPU access.
- Avatar files are mounted from `./assets/avatars` into the container at `/app/assets/avatars`.
- The image is always pulled on container restart (`pull_policy: always`) to stay up to date.
