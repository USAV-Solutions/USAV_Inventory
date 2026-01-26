"""
Product Family schemas.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductFamilyBase(BaseModel):
    """Base product family schema."""
    base_name: str = Field(..., min_length=1, max_length=255, description="Product family name")
    description: Optional[str] = Field(None, max_length=2000, description="Product family description")


class ProductFamilyCreate(ProductFamilyBase):
    """Schema for creating a new product family."""
    product_id: int = Field(..., ge=0, le=99999, description="ECWID product ID (0-99999)")


class ProductFamilyUpdate(BaseModel):
    """Schema for updating a product family."""
    base_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class ProductFamilyResponse(ProductFamilyBase):
    """Schema for product family response."""
    product_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ProductFamilyWithIdentities(ProductFamilyResponse):
    """Product family with associated identities."""
    identities_count: int = Field(default=0, description="Number of product identities")
