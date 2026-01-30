"""API module - Main API configuration."""
from fastapi import APIRouter

from app.api.routes import (
    auth_router,
    bundles_router,
    families_router,
    identities_router,
    inventory_router,
    listings_router,
    variants_router,
)
from app.api.routes.lookups import (
    brand_router,
    color_router,
    condition_router,
    lci_router,
)

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth_router)
api_router.include_router(families_router)
api_router.include_router(identities_router)
api_router.include_router(variants_router)
api_router.include_router(bundles_router)
api_router.include_router(listings_router)
api_router.include_router(inventory_router)
# Lookup routes
api_router.include_router(brand_router)
api_router.include_router(color_router)
api_router.include_router(condition_router)
api_router.include_router(lci_router)

__all__ = ["api_router"]
