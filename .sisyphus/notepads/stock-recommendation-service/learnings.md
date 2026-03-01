

## Task 15: Docker Compose Configuration - Implementation Notes

### Files Created
- `docker-compose.yml` - Main compose file with all services
- `frontend/Dockerfile` - Next.js with Bun container
- `backend/Dockerfile` - FastAPI Python container
- `frontend/.dockerignore` - Excludes node_modules, .next, .git, etc.
- `backend/.dockerignore` - Excludes __pycache__, venv, .git, etc.

### Services Configuration

1. **Frontend Service** (`frontend`):
   - Base image: `oven/bun:1-alpine` (lightweight, fast)
   - Port: 3000
   - Environment: `NEXT_PUBLIC_API_URL=http://localhost:8000`
   - Volumes: Source code mount + anonymous volumes for node_modules/.next
   - Command: `bun run dev` (hot reload enabled)
   - Depends on backend service

2. **Backend Service** (`backend`):
   - Base image: `python:3.11-slim`
   - Port: 8000
   - Environment: `PYTHONUNBUFFERED=1`, `DATA_DIR=/app/data`
   - Volumes: Source code mount + data directory + cache directories
   - Command: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
   - Healthcheck: Checks `/api/health` endpoint every 30s

3. **Batch Service** (`batch`):
   - Uses same Dockerfile as backend
   - Profile: `batch` (not started by default)
   - Command: `python -m batch.scheduler`
   - Volumes: Source code + data directory + logs directory
   - To start: `docker compose --profile batch up`

### Key Design Decisions

1. **Development Mode**: All services run in dev mode with hot reload
   - Frontend: Next.js dev server with volume mounts
   - Backend: Uvicorn with `--reload` flag
   - Volume mounts allow code changes without rebuild

2. **Bun vs npm**: Used Bun for frontend (faster, smaller images)
   - Project already uses bun (bun.lock exists)
   - Alpine-based image for minimal size

3. **Data Sharing**: `/data` directory mounted from host
   - Batch jobs write to `data/`
   - Backend reads from `data/`
   - Persistent storage across container restarts

4. **Anonymous Volumes**: Used for cache directories
   - `/app/node_modules` - Don't overwrite with host
   - `/app/.next` - Persist build cache
   - `/app/__pycache__` - Python bytecode cache

5. **Profiles for Batch**: Optional service using Docker Compose profiles
   - Not started by default (`docker compose up` skips it)
   - Explicitly enable with `--profile batch`
   - Allows running batch on-demand without affecting main services

### Usage Commands

```bash
# Start all main services (frontend + backend)
docker compose up

# Start with batch scheduler
docker compose --profile batch up

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop all services
docker compose down

# Rebuild after Dockerfile changes
docker compose up --build
```

### Network Configuration
- All services on `stock-network` (bridge driver)
- Services can communicate via service names (e.g., `http://backend:8000`)
- Frontend accesses backend via `localhost:8000` (port mapped)
