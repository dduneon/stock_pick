from fastapi import FastAPI

app = FastAPI(
    title="Stock Recommendation API",
    description="Stock recommendation service API",
    version="0.1.0"
)


@app.get("/")
def read_root():
    return {"message": "Stock Recommendation Service API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
