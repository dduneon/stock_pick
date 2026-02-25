from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import stocks

app = FastAPI(
    title="Stock Recommendation API",
    description="Stock recommendation service API",
    version="0.1.0"
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stocks.router)


@app.get("/")
def read_root():
    return {"message": "Stock Recommendation Service API"}


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
