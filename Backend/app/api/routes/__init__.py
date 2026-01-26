"""API routes module."""
from app.api.routes.auth import router as auth_router
from app.api.routes.bundles import router as bundles_router
from app.api.routes.families import router as families_router
from app.api.routes.identities import router as identities_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.listings import router as listings_router
from app.api.routes.variants import router as variants_router

__all__ = [
    "auth_router",
    "bundles_router",
    "families_router",
    "identities_router",
    "inventory_router",
    "listings_router",
    "variants_router",
]
