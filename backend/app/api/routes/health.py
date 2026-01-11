from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.models.schemas import HealthResponse
from app.services.huggingface_service import get_huggingface_service


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.

    Returns the status of the API and its dependencies.
    """
    db_connected = True
    try:
        await db.execute("SELECT 1")
    except Exception:
        db_connected = False

    llm_service = get_huggingface_service()
    model_loaded = llm_service.is_available

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        model_loaded=model_loaded,
        database_connected=db_connected,
        version="1.0.0"
    )
