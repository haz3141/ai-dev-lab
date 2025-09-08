<!-- Version: 0.6.4 -->
# Docker Deployment Guide

This guide covers containerizing and deploying the AI Dev Lab MCP server using Docker with dev and prod profiles.

## Quick Start

### Prerequisites
- Docker Desktop installed and running
- Python project with requirements.txt
- `.env` file configured (copy from `.env.sample`)

### Dev Profile (Hot Reload)
```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Run with hot reload
docker compose --profile dev up --build
```

### Prod Profile (Optimized)
```bash
# Build once
docker compose build

# Run production container
docker compose --profile prod up -d
```

## Files Overview

### .dockerignore
Excludes unnecessary files from Docker context for faster builds:
- Git files, cache directories, logs
- Python bytecode and virtual environments
- Node modules and build artifacts

### Dockerfile
Multi-stage build with security best practices:
- **Base stage**: Python slim image with system dependencies
- **Builder stage**: Installs Python dependencies in virtual environment
- **Runtime stage**: Non-root user (UID 10001), minimal attack surface

### compose.yaml
Two profiles for different environments:

#### Dev Profile
- Live reload with `--reload` flag
- Bind mount source code (`./:/app`)
- Hot reload on file changes
- Health checks enabled

#### Prod Profile
- Optimized image without source mounts
- Production-ready with restart policies
- Same health checks as dev

### .env Configuration
```bash
# Copy from .env.sample and configure
cp .env.sample .env

# Required variables
OPENAI_API_KEY=your_api_key_here
PORT=8765
PYTHONUNBUFFERED=1
WORKERS=2
```

## Security Features

### Non-Root Execution
- Runtime container runs as user `appuser` (UID 10001)
- No privileged access to host system
- Minimal attack surface

### Secret Management
- Environment variables for sensitive data
- No secrets baked into images
- `.env` file excluded from version control

### Health Checks
- Built-in health endpoint at `/healthz`
- Container health monitoring
- Automatic restart on failures

## Build Optimization

### BuildKit Enabled
```bash
export DOCKER_BUILDKIT=1
docker buildx create --use
```

Benefits:
- Parallel build stages
- Better layer caching
- Faster incremental builds

### Multi-Stage Build
- Separate builder and runtime images
- Smaller final image size
- Dependencies isolated from source code

## MCP Integration

### Cursor Configuration
Updated `.cursor/mcp.json` to include Docker server:
```json
{
  "mcpServers": {
    "lab-server": {
      "command": ".venv/bin/python",
      "args": ["-m", "mcp_server.simple_server"]
    },
    "dev-lab-server": {
      "command": "curl",
      "args": ["-s", "http://127.0.0.1:8765"]
    }
  }
}
```

### Health Verification
```bash
# Test health endpoint
curl -fsS http://127.0.0.1:8765/healthz

# Expected response
{"ok": true, "version": "0.6.4"}
```

## Troubleshooting

### Container Won't Start
1. Check Docker Desktop is running
2. Verify `.env` file exists and has required variables
3. Check logs: `docker compose --profile dev logs`
4. Ensure port 8765 is not in use

### Health Check Fails
1. Verify MCP server can start locally first
2. Check health endpoint: `curl http://127.0.0.1:8765/healthz`
3. Review container logs for import errors

### Build Fails
1. Ensure BuildKit is enabled: `export DOCKER_BUILDKIT=1`
2. Check requirements.txt for missing dependencies
3. Verify Python version compatibility (3.11)

### MCP Connection Issues
1. Confirm container is running: `docker compose --profile dev ps`
2. Test health endpoint manually
3. Check Cursor MCP panel for connection status
4. Verify port mapping in compose.yaml

## Production Deployment

### Image Registry
```bash
# Tag for registry
docker tag dev-lab/mcp-lab:local your-registry.com/dev-lab/mcp-lab:v0.6.4

# Push to registry
docker push your-registry.com/dev-lab/mcp-lab:v0.6.4
```

### Kubernetes Deployment
The container is ready for Kubernetes with:
- Health checks for liveness/readiness probes
- Non-root security context
- Environment-based configuration
- Structured logging support

### Cloud Deployment
For cloud platforms (AWS, GCP, Azure):
1. Use registry-hosted images
2. Configure secrets management
3. Set up load balancers
4. Configure monitoring and logging

## Performance Tuning

### Workers
Adjust `WORKERS` in `.env` based on CPU cores:
```bash
# For 4-core machine
WORKERS=4
```

### Memory Limits
```yaml
# In compose.yaml
services:
  mcp-lab:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

### Health Check Tuning
```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:${PORT}/healthz"]
  interval: 30s      # Check every 30 seconds
  timeout: 10s       # Fail after 10 seconds
  retries: 3         # Retry 3 times before marking unhealthy
  start_period: 40s  # Wait 40s for startup
```

## Monitoring & Observability

### Logs
```bash
# View logs
docker compose --profile dev logs -f

# Follow logs
docker compose --profile dev logs -f mcp-lab
```

### Metrics
- Container resource usage: `docker stats`
- Application health: `/healthz` endpoint
- MCP server metrics: Integrated with existing audit logging

### Debugging
```bash
# Enter running container
docker compose --profile dev exec mcp-lab bash

# Check processes
docker compose --profile dev exec mcp-lab ps aux

# View environment
docker compose --profile dev exec mcp-lab env
```

## Next Steps

1. **Test locally**: Run dev profile and verify MCP tools work in Cursor
2. **Build CI/CD**: Add GitHub Actions for automated builds
3. **Add monitoring**: Integrate with observability stack
4. **Scale**: Deploy to Kubernetes or cloud platform
5. **Promote**: Move from lab to app directory with production configuration

## Files Created/Modified

- ✅ `.dockerignore` - Docker build exclusions
- ✅ `.env.sample` - Environment template
- ✅ `Dockerfile` - Multi-stage container definition
- ✅ `compose.yaml` - Dev/prod profiles
- ✅ `.cursor/mcp.json` - Updated MCP configuration
- ✅ `docs/deployment/docker-deployment.md` - This documentation

## Checkpoint Status

- **Dev Profile**: Ready for local development with hot reload
- **Prod Profile**: Optimized for production deployment
- **Security**: Non-root, secrets via env, health checks
- **MCP Integration**: Cursor configuration updated
- **Documentation**: Complete deployment guide created

The containerized MCP server is ready for both development and production use cases.
