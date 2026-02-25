from fastapi import APIRouter

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("")
def get_stocks():
    """Get all stocks (empty array initially)"""
    return []
