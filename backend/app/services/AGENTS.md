# backend/app/services

## OVERVIEW
Business logic layer - stock data processing, recommendations, and technical analysis.

## FILES
- `recommendation.py` - Core stock recommendation algorithm
- `technical_analysis.py` - Technical indicators (SMA, EMA, RSI, MACD)
- `data_loader.py` - Loads stock data from JSON files
- `data_quality.py` - Data validation and quality checks
- `dart_api.py` - External DART API integration

## WHERE TO LOOK
| Task | File |
|------|------|
| Modify recommendation logic | `recommendation.py` |
| Add technical indicator | `technical_analysis.py` |
| Load stock data | `data_loader.py` |

## CONVENTIONS
- Service functions return typed data (Pydantic models)
- Data loading cached where appropriate
- Technical analysis uses pandas/numpy

## ANTI-PATTERNS
- NO direct JSON file access outside data_loader
- NO hardcoded API keys in code
