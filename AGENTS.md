# PROJECT KNOWLEDGE BASE

**Generated:** 2026-02-28
**Commit:** 37e672e
**Branch:** master

## OVERVIEW
Full-stack stock recommendation web application. FastAPI backend serves stock data + recommendations; Next.js 15 frontend displays charts, search, and stock details.

## STRUCTURE
```
./
├── backend/           # FastAPI REST API
│   ├── app/
│   │   ├── routers/   # API endpoints (stocks)
│   │   ├── services/  # Business logic (recommendation, technical analysis)
│   │   └── schemas/   # Pydantic models
│   ├── batch/         # Scheduled data updates
│   ├── tests/         # Backend tests
│   └── main.py        # Entry point
├── frontend/          # Next.js 15 SPA
│   ├── app/           # Pages (home, stocks, search, stock/[ticker])
│   ├── components/    # UI components
│   ├── e2e/           # Playwright tests
│   ├── lib/           # Utilities
│   └── types/         # TypeScript types
└── data/              # Stock data files
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add API endpoint | `backend/app/routers/stocks.py` | Add route, register in `__init__.py` |
| Add recommendation logic | `backend/app/services/recommendation.py` | Core algorithm |
| Add frontend page | `frontend/app/` | Next.js App Router |
| Add UI component | `frontend/components/` | React components |
| Run backend | `backend/main.py` | FastAPI dev server |
| Run frontend | `frontend/` | `bun run dev` |
| Run tests | Root | `pytest` / `playwright test` |

## CONVENTIONS
- **Backend**: FastAPI with Pydantic schemas, services layer pattern
- **Frontend**: Next.js App Router, Tailwind CSS, CVA for variants
- **Testing**: Playwright for e2e, pytest for backend
- **Data**: JSON files in `data/`, loaded via `data_loader.py`

## ANTI-PATTERNS (THIS PROJECT)
- NO `as any` or `@ts-ignore` in TypeScript
- NO bare `except:` in Python
- NO commit without running tests first

## COMMANDS
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend && bun install && bun run dev

# Docker
docker compose up -d

# Tests
pytest backend/
playwright test frontend/e2e/
```

## NOTES
- Frontend runs on WSL2 directly (not Docker) for easier Windows browser access
- API URL: `NEXT_PUBLIC_API_URL=http://localhost:8000`
- Health check: `GET /api/health`
