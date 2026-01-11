from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from app.models.database import get_db
from app.models.schemas import (
    PhoneResponse, PhoneListResponse,
    SearchRequest, SearchResponse,
    CompareRequest, CompareResponse
)
from app.core.agent import ShoppingAgent
from app.repositories.phone_repository import PhoneRepository
from app.services.product_service import get_product_service


router = APIRouter()


@router.get("", response_model=PhoneListResponse)
async def get_products(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    min_price: Optional[int] = Query(None, description="Minimum price in INR"),
    max_price: Optional[int] = Query(None, description="Maximum price in INR"),
    min_ram: Optional[int] = Query(None, description="Minimum RAM in GB"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Results offset"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of products with optional filters.

    Returns paginated list of mobile phones.
    """
    phone_repo = PhoneRepository(db)
    product_service = get_product_service()

    if brand or min_price or max_price or min_ram:
        phones = await phone_repo.search(
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            min_ram=min_ram,
            limit=limit
        )
    else:
        phones = await phone_repo.get_all(limit=limit, offset=offset)

    phone_responses = product_service.phones_to_response(phones)

    return PhoneListResponse(
        products=phone_responses,
        count=len(phone_responses)
    )


@router.get("/{phone_id}", response_model=PhoneResponse)
async def get_product(
    phone_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get details for a specific phone.

    - **phone_id**: The ID of the phone to retrieve
    """
    phone_repo = PhoneRepository(db)
    product_service = get_product_service()

    phone = await phone_repo.get_by_id(phone_id)
    if not phone:
        raise HTTPException(
            status_code=404,
            detail=f"Phone with ID {phone_id} not found"
        )

    return product_service.phone_to_response(phone)


@router.post("/search", response_model=SearchResponse)
async def search_products(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search products with natural language query.

    - **query**: Natural language search query
    - **filters**: Optional filters (brand, price range, etc.)
    """
    agent = ShoppingAgent(db)
    result = await agent.search_phones(
        query=request.query,
        filters=request.filters
    )

    return SearchResponse(
        products=result["products"],
        explanation=result["explanation"],
        count=result["count"]
    )


@router.post("/compare", response_model=CompareResponse)
async def compare_products(
    request: CompareRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compare multiple phones.

    - **product_ids**: List of phone IDs to compare (2-4 phones)
    """
    if len(request.product_ids) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 phone IDs required for comparison"
        )

    if len(request.product_ids) > 4:
        raise HTTPException(
            status_code=400,
            detail="Maximum 4 phones can be compared at once"
        )

    agent = ShoppingAgent(db)
    result = await agent.compare_phones(request.product_ids)

    if not result["phones"]:
        raise HTTPException(
            status_code=404,
            detail="One or more phones not found"
        )

    return CompareResponse(
        phones=result["phones"],
        comparison=result["comparison"],
        summary=result["summary"],
        recommendation=None
    )


@router.get("/brand/{brand}", response_model=PhoneListResponse)
async def get_products_by_brand(
    brand: str,
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """
    Get phones by brand.

    - **brand**: Brand name (Samsung, OnePlus, Xiaomi, etc.)
    """
    phone_repo = PhoneRepository(db)
    product_service = get_product_service()

    phones = await phone_repo.get_by_brand(brand, limit)
    phone_responses = product_service.phones_to_response(phones)

    return PhoneListResponse(
        products=phone_responses,
        count=len(phone_responses)
    )


@router.get("/category/flagship", response_model=PhoneListResponse)
async def get_flagship_phones(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get flagship phones (premium tier)."""
    phone_repo = PhoneRepository(db)
    product_service = get_product_service()

    phones = await phone_repo.get_flagship_phones(limit=limit)
    phone_responses = product_service.phones_to_response(phones)

    return PhoneListResponse(
        products=phone_responses,
        count=len(phone_responses)
    )


@router.get("/category/budget", response_model=PhoneListResponse)
async def get_budget_phones(
    max_price: int = Query(20000, description="Maximum price in INR"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get budget phones."""
    phone_repo = PhoneRepository(db)
    product_service = get_product_service()

    phones = await phone_repo.get_budget_phones(max_price, limit)
    phone_responses = product_service.phones_to_response(phones)

    return PhoneListResponse(
        products=phone_responses,
        count=len(phone_responses)
    )


@router.get("/category/gaming", response_model=PhoneListResponse)
async def get_gaming_phones(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get gaming phones (high refresh rate, good performance)."""
    phone_repo = PhoneRepository(db)
    product_service = get_product_service()

    phones = await phone_repo.get_gaming_phones(limit=limit)
    phone_responses = product_service.phones_to_response(phones)

    return PhoneListResponse(
        products=phone_responses,
        count=len(phone_responses)
    )


@router.get("/category/camera", response_model=PhoneListResponse)
async def get_camera_phones(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    """Get camera-focused phones."""
    phone_repo = PhoneRepository(db)
    product_service = get_product_service()

    phones = await phone_repo.get_camera_phones(limit=limit)
    phone_responses = product_service.phones_to_response(phones)

    return PhoneListResponse(
        products=phone_responses,
        count=len(phone_responses)
    )
