"""Models module - Export all SQLAlchemy models."""
try:
    from app.models.entities import (
        Base,
        BundleComponent,
        BundleRole,
        ConditionCode,
        IdentityType,
        InventoryItem,
        InventoryStatus,
        PhysicalClass,
        Platform,
        PlatformListing,
        PlatformSyncStatus,
        ProductFamily,
        ProductIdentity,
        ProductVariant,
        ZohoSyncStatus,
    )
except ImportError as e:
    print(f"Failed to import from entities: {e}")
    raise

try:
    from app.models.user import User, UserRole
except ImportError as e:
    print(f"Failed to import from user: {e}")
    raise

__all__ = [
    # Base
    "Base",
    # Enums
    "IdentityType",
    "PhysicalClass",
    "ConditionCode",
    "ZohoSyncStatus",
    "PlatformSyncStatus",
    "InventoryStatus",
    "BundleRole",
    "Platform",
    "UserRole",
    # Models
    "ProductFamily",
    "ProductIdentity",
    "ProductVariant",
    "BundleComponent",
    "PlatformListing",
    "InventoryItem",
    "User",
]
