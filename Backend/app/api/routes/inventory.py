"""
Inventory API endpoints.
Handles InventoryItem CRUD and status management.
"""
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import InventoryStatus
from app.repositories import InventoryItemRepository, ProductVariantRepository
from app.schemas import (
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
    InventoryItemWithVariant,
    InventorySummary,
    PaginatedResponse,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=PaginatedResponse)
async def list_inventory(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    variant_id: Annotated[int | None, Query(description="Filter by variant")] = None,
    status_filter: Annotated[InventoryStatus | None, Query(alias="status", description="Filter by status")] = None,
    location_code: Annotated[str | None, Query(description="Filter by location")] = None,
    db: AsyncSession = Depends(get_db),
):
    """List inventory items with optional filtering."""
    repo = InventoryItemRepository(db)
    
    filters = {}
    if variant_id is not None:
        filters["variant_id"] = variant_id
    if status_filter is not None:
        filters["status"] = status_filter
    if location_code is not None:
        filters["location_code"] = location_code
    
    items = await repo.get_multi(skip=skip, limit=limit, filters=filters, order_by="id")
    total = await repo.count(filters=filters)
    
    return PaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[InventoryItemResponse.model_validate(item) for item in items]
    )


@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new inventory item."""
    inventory_repo = InventoryItemRepository(db)
    variant_repo = ProductVariantRepository(db)
    
    # Verify variant exists
    variant = await variant_repo.get(data.variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product variant {data.variant_id} not found"
        )
    
    # Check for duplicate serial number
    if data.serial_number:
        existing = await inventory_repo.get_by_serial(data.serial_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Inventory item with serial '{data.serial_number}' already exists"
            )
    
    item = await inventory_repo.create(data.model_dump())
    return InventoryItemResponse.model_validate(item)


@router.get("/{item_id}", response_model=InventoryItemWithVariant)
async def get_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get an inventory item by ID."""
    repo = InventoryItemRepository(db)
    item = await repo.get(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item {item_id} not found"
        )
    
    return InventoryItemWithVariant.model_validate(item)


@router.get("/serial/{serial_number}", response_model=InventoryItemResponse)
async def get_inventory_by_serial(
    serial_number: str,
    db: AsyncSession = Depends(get_db),
):
    """Get an inventory item by serial number."""
    repo = InventoryItemRepository(db)
    item = await repo.get_by_serial(serial_number)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item with serial '{serial_number}' not found"
        )
    
    return InventoryItemResponse.model_validate(item)


@router.patch("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update an inventory item."""
    repo = InventoryItemRepository(db)
    item = await repo.get(item_id)
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item {item_id} not found"
        )
    
    # Check for duplicate serial if changing it
    if data.serial_number and data.serial_number != item.serial_number:
        existing = await repo.get_by_serial(data.serial_number)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Inventory item with serial '{data.serial_number}' already exists"
            )
    
    update_data = data.model_dump(exclude_unset=True)
    if update_data:
        item = await repo.update(item, update_data)
    
    return InventoryItemResponse.model_validate(item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an inventory item."""
    repo = InventoryItemRepository(db)
    
    deleted = await repo.delete(item_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inventory item {item_id} not found"
        )


@router.post("/{item_id}/reserve", response_model=InventoryItemResponse)
async def reserve_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Reserve an available inventory item."""
    repo = InventoryItemRepository(db)
    
    item = await repo.reserve_item(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reserve item {item_id} - not available or doesn't exist"
        )
    
    return InventoryItemResponse.model_validate(item)


@router.post("/{item_id}/sell", response_model=InventoryItemResponse)
async def sell_inventory_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Mark an inventory item as sold."""
    repo = InventoryItemRepository(db)
    
    item = await repo.sell_item(item_id, sold_at=datetime.now())
    if not item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot sell item {item_id} - not available/reserved or doesn't exist"
        )
    
    return InventoryItemResponse.model_validate(item)


@router.get("/summary/{variant_id}", response_model=InventorySummary)
async def get_inventory_summary(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get inventory count summary for a variant."""
    inventory_repo = InventoryItemRepository(db)
    variant_repo = ProductVariantRepository(db)
    
    variant = await variant_repo.get(variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product variant {variant_id} not found"
        )
    
    counts = await inventory_repo.count_by_status(variant_id)
    
    return InventorySummary(
        variant_id=variant_id,
        full_sku=variant.full_sku,
        available=counts.get("AVAILABLE", 0),
        sold=counts.get("SOLD", 0),
        reserved=counts.get("RESERVED", 0),
        rma=counts.get("RMA", 0),
        damaged=counts.get("DAMAGED", 0),
        total=counts.get("total", 0)
    )


@router.get("/value/total", response_model=dict)
async def get_total_inventory_value(
    variant_id: Annotated[int | None, Query(description="Filter by variant")] = None,
    status_filter: Annotated[InventoryStatus | None, Query(alias="status")] = None,
    db: AsyncSession = Depends(get_db),
):
    """Calculate total inventory value (cost basis)."""
    repo = InventoryItemRepository(db)
    
    total = await repo.get_total_value(variant_id=variant_id, status=status_filter)
    
    return {
        "total_value": total,
        "currency": "USD",
        "filters": {
            "variant_id": variant_id,
            "status": status_filter.value if status_filter else None
        }
    }
