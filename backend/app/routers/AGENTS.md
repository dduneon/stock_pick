# backend/app/routers

## OVERVIEW
FastAPI route handlers - stock API endpoints.

## FILES
- `stocks.py` - Stock API endpoints (list, search, detail, recommendations)
- `__init__.py` - Router registration

## ENDPOINTS
| Method | Path | Description |
|--------|------|-------------|
| GET | `/stocks` | List all stocks |
| GET | `/stocks/search` | Search stocks |
| GET | `/stocks/{ticker}` | Stock detail |
| GET | `/stocks/{ticker}/recommendations` | Stock recommendations |

## CONVENTIONS
- Routes return Pydantic schemas
- Error handling via HTTPException
- Async endpoints where applicable

## ANTI-PATTERNS
- NO bare `except:` - catch specific exceptions
- NO return raw dictionaries - use schemas
