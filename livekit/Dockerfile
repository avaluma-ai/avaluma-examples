FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu24.04 AS runtime

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including EGL support
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    git \
    build-essential \
    # EGL and OpenGL support
    libegl1 \
    libgl1 \
    libgles2 \
    libglvnd0 \
    libglvnd-dev \
    # Audio support
    libsndfile1 \
    libportaudio2 \
    # Python 3.12
    python3.12 \
    python3.12-dev \
    python3.12-venv \
    python-is-python3 \
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# EGL vendor configuration für NVIDIA
RUN mkdir -p /usr/share/glvnd/egl_vendor.d && \
    echo '{"file_format_version" : "1.0.0", "ICD" : {"library_path" : "libEGL_nvidia.so.0"}}' \
    > /usr/share/glvnd/egl_vendor.d/10_nvidia.json

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN uv sync
RUN uv pip install git+https://github.com/avaluma-ai/avaluma-livekit-plugin.git

# Pre-download any ML models or files the agent needs
# This ensures the container is ready to run immediately without downloading
# dependencies at runtime, which improves startup time and reliability
COPY src/utils src/utils
RUN uv run src/utils/download_plugin_files.py

# Run the application using UV
# UV will activate the virtual environment and run the agent.
# The "start" command tells the worker to connect to LiveKit and begin waiting for jobs.
ENTRYPOINT ["uv", "run", "python", "src/agent.py", "start"]
