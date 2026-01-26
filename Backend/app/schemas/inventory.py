"""
Inventory Item schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import InventoryStatus


class InventoryItemBase(BaseModel):
    """Base inventory item schema."""
    serial_number: Optional[str] = Field(None, max_length=100, description="Manufacturer serial number")
    status: InventoryStatus = Field(default=InventoryStatus.AVAILABLE, description="Item status")
    location_code: Optional[str] = Field(None, max_length=50, description="Warehouse location")
    cost_basis: Optional[float] = Field(None, ge=0, description="Acquisition cost")
    notes: Optional[str] = Field(None, description="Additional notes")


class InventoryItemCreate(InventoryItemBase):
    """Schema for creating an inventory item."""
    variant_id: int = Field(..., description="Link to product variant")


class InventoryItemUpdate(BaseModel):
    """Schema for updating an inventory item."""
    serial_number: Optional[str] = Field(None, max_length=100)
    status: Optional[InventoryStatus] = Field(None)
    location_code: Optional[str] = Field(None, max_length=50)
    cost_basis: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None)


class InventoryItemResponse(InventoryItemBase):
    """Schema for inventory item response."""
    id: int
    variant_id: int
    received_at: Optional[datetime] = None
    sold_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class InventoryItemWithVariant(InventoryItemResponse):
    """Inventory item with variant SKU info."""
    full_sku: Optional[str] = Field(None, description="SKU of the variant")


class InventorySummary(BaseModel):
    """Summary of inventory counts by status."""
    total_items: int = Field(default=0)
    available: int = Field(default=0)
    sold: int = Field(default=0)
    reserved: int = Field(default=0)
    rma: int = Field(default=0)
    damaged: int = Field(default=0)
