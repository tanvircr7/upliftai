# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    UV_LINK_MODE=copy

# OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates build-essential git \
 && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# ----- deps (creates /app/.venv) -----
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --compile-bytecode

# activate the uv-created venv for all subsequent commands
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ----- app code -----
COPY src ./src
COPY .env.example ./.env.example
ENV PYTHONPATH="/app/src"

# proper non-root user & writable home (CrewAI writes to XDG dirs)
RUN useradd -m -d /home/appuser -s /bin/bash appuser
ENV HOME=/home/appuser \
    XDG_DATA_HOME=/home/appuser/.local/share
RUN mkdir -p "$XDG_DATA_HOME" && chown -R appuser:appuser /home/appuser /app

USER appuser

ENTRYPOINT ["python", "-m", "upliftai.main"]
