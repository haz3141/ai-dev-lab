# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.11

FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps (curl only for health/debug)
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# === builder for deterministic wheels ===
FROM base AS builder
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

# Respect pinned deps if present
COPY requirements.txt /app/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip wheel setuptools && \
    pip install -r /app/requirements.txt

# === runtime image (non-root) ===
FROM base AS runtime
# Add a non-root user (10001)
RUN useradd -m -u 10001 appuser
ENV PATH="/opt/venv/bin:${PATH}"
COPY --from=builder /opt/venv /opt/venv

# Copy source
COPY . /app

# Drop privileges
USER 10001:10001

# Default envs (can override via compose)
ENV PORT=8765 \
    WORKERS=2 \
    UVICORN_LOG_LEVEL=info

# Health endpoint assumed at /healthz (FastAPI)
HEALTHCHECK --interval=10s --timeout=2s --retries=6 CMD curl -fsS http://127.0.0.1:${PORT}/healthz || exit 1

EXPOSE ${PORT}

# Signal handling for graceful shutdown
STOPSIGNAL SIGTERM

# Use ENTRYPOINT exec-form for proper signal handling (becomes PID 1)
ENTRYPOINT ["/opt/venv/bin/uvicorn"]

# Default args (can be overridden)
CMD ["mcp_server.server:app", "--host", "0.0.0.0", "--port", "8765", "--workers", "2", "--proxy-headers"]
