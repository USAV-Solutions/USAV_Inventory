"""
API Testing Script for USAV Inventory System
Comprehensive endpoint testing using pytest and httpx
"""
import asyncio
import pytest
from httpx import AsyncClient, Client

from app.main import app
from app.core.config import settings


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Synchronous HTTP client for testing."""
    return Client(app=app, base_url="http://test")


@pytest.fixture
async def async_client():
    """Asynchronous HTTP client for testing."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_create_user_admin(self, client):
        """Test creating a new admin user."""
        response = client.post(
            "/api/v1/auth/users",
            json={
                "username": "admin_user",
                "password": "SecurePassword123!",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "role": "ADMIN"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "admin_user"
        assert data["role"] == "ADMIN"
        assert "id" in data
    
    def test_create_user_warehouse_op(self, client):
        """Test creating a warehouse operator user."""
        response = client.post(
            "/api/v1/auth/users",
            json={
                "username": "warehouse_op",
                "password": "SecurePassword123!",
                "full_name": "Warehouse Operator",
                "role": "WAREHOUSE_OP"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "WAREHOUSE_OP"
    
    def test_login_success(self, client):
        """Test successful login."""
        # First create a user
        client.post(
            "/api/v1/auth/users",
            json={
                "username": "testuser",
                "password": "TestPassword123!",
                "role": "SALES_REP"
            }
        )
        
        # Then login
        response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "testuser",
                "password": "TestPassword123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_get_current_user(self, client):
        """Test getting current user info."""
        # Create and login a user
        client.post(
            "/api/v1/auth/users",
            json={
                "username": "currentuser",
                "password": "CurrentPass123!",
                "role": "ADMIN"
            }
        )
        
        login_response = client.post(
            "/api/v1/auth/token",
            data={
                "username": "currentuser",
                "password": "CurrentPass123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Get current user
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "currentuser"


# ============================================================================
# PRODUCT FAMILY TESTS
# ============================================================================

class TestProductFamilies:
    """Test product family endpoints."""
    
    def test_create_product_family(self, client):
        """Test creating a product family."""
        response = client.post(
            "/api/v1/families",
            json={
                "product_id": 845,
                "base_name": "Bose 201 Series",
                "description": "Compact speakers with excellent sound quality"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == 845
        assert data["base_name"] == "Bose 201 Series"
    
    def test_list_product_families(self, client):
        """Test listing product families."""
        # Create a family first
        client.post(
            "/api/v1/families",
            json={
                "product_id": 846,
                "base_name": "Test Family"
            }
        )
        
        response = client.get("/api/v1/families")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
    
    def test_get_product_family(self, client):
        """Test getting a specific product family."""
        # Create a family
        create_response = client.post(
            "/api/v1/families",
            json={
                "product_id": 847,
                "base_name": "Get Test Family"
            }
        )
        
        product_id = create_response.json()["product_id"]
        response = client.get(f"/api/v1/families/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == product_id
    
    def test_update_product_family(self, client):
        """Test updating a product family."""
        # Create a family
        create_response = client.post(
            "/api/v1/families",
            json={
                "product_id": 848,
                "base_name": "Original Name"
            }
        )
        
        product_id = create_response.json()["product_id"]
        response = client.put(
            f"/api/v1/families/{product_id}",
            json={"base_name": "Updated Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["base_name"] == "Updated Name"
    
    def test_delete_product_family(self, client):
        """Test deleting a product family."""
        # Create a family
        create_response = client.post(
            "/api/v1/families",
            json={
                "product_id": 849,
                "base_name": "Delete Test"
            }
        )
        
        product_id = create_response.json()["product_id"]
        response = client.delete(f"/api/v1/families/{product_id}")
        assert response.status_code == 204


# ============================================================================
# PRODUCT IDENTITY TESTS
# ============================================================================

class TestProductIdentities:
    """Test product identity endpoints."""
    
    def test_create_product_identity(self, client):
        """Test creating a product identity."""
        # First create a family
        family_response = client.post(
            "/api/v1/families",
            json={
                "product_id": 850,
                "base_name": "Identity Test Family"
            }
        )
        
        # Then create an identity
        response = client.post(
            "/api/v1/identities",
            json={
                "product_id": 850,
                "type": "Base",
                "physical_class": "E"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == 850
        assert data["type"] == "Base"
    
    def test_create_part_identity(self, client):
        """Test creating a Part identity with LCI."""
        # Create family first
        client.post(
            "/api/v1/families",
            json={
                "product_id": 851,
                "base_name": "Part Test Family"
            }
        )
        
        response = client.post(
            "/api/v1/identities",
            json={
                "product_id": 851,
                "type": "P",
                "lci": 1,
                "physical_class": "C"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "P"
        assert data["lci"] == 1
    
    def test_list_product_identities(self, client):
        """Test listing product identities."""
        response = client.get("/api/v1/identities")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


# ============================================================================
# PRODUCT VARIANT TESTS
# ============================================================================

class TestProductVariants:
    """Test product variant endpoints."""
    
    def test_create_product_variant(self, client):
        """Test creating a product variant."""
        # Create family and identity first
        family_response = client.post(
            "/api/v1/families",
            json={
                "product_id": 852,
                "base_name": "Variant Test Family"
            }
        )
        
        identity_response = client.post(
            "/api/v1/identities",
            json={
                "product_id": 852,
                "type": "Base"
            }
        )
        identity_id = identity_response.json()["id"]
        
        # Create variant
        response = client.post(
            "/api/v1/variants",
            json={
                "identity_id": identity_id,
                "color_code": "BK",
                "condition_code": "N"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["identity_id"] == identity_id
        assert data["color_code"] == "BK"
    
    def test_list_product_variants(self, client):
        """Test listing product variants."""
        response = client.get("/api/v1/variants")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data


# ============================================================================
# BUNDLE COMPONENT TESTS
# ============================================================================

class TestBundleComponents:
    """Test bundle component endpoints."""
    
    def test_create_bundle_component(self, client):
        """Test creating a bundle component."""
        # Create two families and identities
        family1 = client.post(
            "/api/v1/families",
            json={"product_id": 853, "base_name": "Bundle Parent"}
        ).json()
        
        family2 = client.post(
            "/api/v1/families",
            json={"product_id": 854, "base_name": "Bundle Child"}
        ).json()
        
        identity1 = client.post(
            "/api/v1/identities",
            json={"product_id": 853, "type": "B"}
        ).json()
        
        identity2 = client.post(
            "/api/v1/identities",
            json={"product_id": 854, "type": "Base"}
        ).json()
        
        # Create bundle component
        response = client.post(
            "/api/v1/bundles",
            json={
                "parent_identity_id": identity1["id"],
                "child_identity_id": identity2["id"],
                "quantity_required": 2,
                "role": "Primary"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["quantity_required"] == 2
        assert data["role"] == "Primary"


# ============================================================================
# PLATFORM LISTING TESTS
# ============================================================================

class TestPlatformListings:
    """Test platform listing endpoints."""
    
    def test_create_platform_listing(self, client):
        """Test creating a platform listing."""
        # Create family, identity, and variant first
        family_response = client.post(
            "/api/v1/families",
            json={"product_id": 855, "base_name": "Listing Test"}
        )
        
        identity_response = client.post(
            "/api/v1/identities",
            json={"product_id": 855, "type": "Base"}
        )
        
        variant_response = client.post(
            "/api/v1/variants",
            json={
                "identity_id": identity_response.json()["id"],
                "color_code": "SV"
            }
        )
        variant_id = variant_response.json()["id"]
        
        # Create platform listing
        response = client.post(
            "/api/v1/listings",
            json={
                "variant_id": variant_id,
                "platform": "AMAZON_US",
                "external_ref_id": "ASIN123456",
                "listing_price": 99.99
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["platform"] == "AMAZON_US"
        assert data["listing_price"] == 99.99


# ============================================================================
# INVENTORY TESTS
# ============================================================================

class TestInventoryItems:
    """Test inventory item endpoints."""
    
    def test_create_inventory_item(self, client):
        """Test creating an inventory item."""
        # Create family, identity, and variant first
        client.post(
            "/api/v1/families",
            json={"product_id": 856, "base_name": "Inventory Test"}
        )
        
        identity_response = client.post(
            "/api/v1/identities",
            json={"product_id": 856, "type": "Base"}
        )
        
        variant_response = client.post(
            "/api/v1/variants",
            json={"identity_id": identity_response.json()["id"]}
        )
        variant_id = variant_response.json()["id"]
        
        # Create inventory item
        response = client.post(
            "/api/v1/inventory",
            json={
                "variant_id": variant_id,
                "serial_number": "SN123456789",
                "status": "AVAILABLE",
                "location_code": "A1-S2",
                "cost_basis": 45.50
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["serial_number"] == "SN123456789"
        assert data["status"] == "AVAILABLE"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test error handling and validation."""
    
    def test_create_family_invalid_product_id(self, client):
        """Test creating family with invalid product ID."""
        response = client.post(
            "/api/v1/families",
            json={
                "product_id": 100000,  # Out of range (0-99999)
                "base_name": "Invalid"
            }
        )
        assert response.status_code == 422
    
    def test_create_identity_nonexistent_family(self, client):
        """Test creating identity for nonexistent family."""
        response = client.post(
            "/api/v1/identities",
            json={
                "product_id": 99999,
                "type": "Base"
            }
        )
        assert response.status_code in [404, 422]
    
    def test_get_nonexistent_family(self, client):
        """Test getting nonexistent family."""
        response = client.get("/api/v1/families/99999")
        assert response.status_code == 404
    
    def test_invalid_user_role(self, client):
        """Test creating user with invalid role."""
        response = client.post(
            "/api/v1/auth/users",
            json={
                "username": "invalid_role",
                "password": "Password123!",
                "role": "INVALID_ROLE"
            }
        )
        assert response.status_code == 422


if __name__ == "__main__":
    # Run tests with: pytest tests/test_api.py -v
    pytest.main([__file__, "-v", "--tb=short"])
