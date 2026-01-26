"""
Manual API Testing Script - No pytest required
Run this script to manually test all API endpoints
"""
import httpx
import json
import time
from typing import Dict, Any, Optional


class APITester:
    """API tester for USAV Inventory System."""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_prefix = "/api/v1"
        self.token: Optional[str] = None
        self.client = httpx.Client()
        self.results = []
    
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test result."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   └─ {details}")
    
    def make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict] = None,
        data: Optional[Dict] = None,
        expected_status: int = 200,
        test_name: str = ""
    ) -> Optional[Dict]:
        """Make HTTP request and check status."""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        headers = {}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        try:
            if method == "GET":
                response = self.client.get(url, headers=headers)
            elif method == "POST":
                response = self.client.post(url, json=json_data, data=data, headers=headers)
            elif method == "PUT":
                response = self.client.put(url, json=json_data, headers=headers)
            elif method == "DELETE":
                response = self.client.delete(url, headers=headers)
            else:
                self.log_test(test_name, "FAIL", f"Unknown method: {method}")
                return None
            
            if response.status_code == expected_status:
                self.log_test(
                    test_name,
                    "PASS",
                    f"{method} {endpoint} -> {response.status_code}"
                )
                try:
                    return response.json()
                except:
                    return {"status": "success"}
            else:
                self.log_test(
                    test_name,
                    "FAIL",
                    f"{method} {endpoint} -> Expected {expected_status}, got {response.status_code}"
                )
                try:
                    print(f"      Response: {response.json()}")
                except:
                    print(f"      Response: {response.text}")
                return None
        
        except Exception as e:
            self.log_test(test_name, "ERROR", str(e))
            return None
    
    # ========================================================================
    # AUTHENTICATION TESTS
    # ========================================================================
    
    def test_authentication(self):
        """Test authentication endpoints."""
        print("\n" + "="*70)
        print("AUTHENTICATION TESTS")
        print("="*70)
        
        # Login
        login_response = self.make_request(
            "POST",
            "/auth/token",
            data={
                "username": "sysad",
                "password": "bach9999"
            },
            test_name="Login"
        )
        
        if login_response and "access_token" in login_response:
            self.token = login_response["access_token"]
            print(f"   └─ Token obtained: {self.token[:20]}...")
        
        # Get current user
        self.make_request(
            "GET",
            "/auth/me",
            test_name="Get Current User"
        )
    
    # ========================================================================
    # PRODUCT FAMILY TESTS
    # ========================================================================
    
    def test_product_families(self):
        """Test product family endpoints."""
        print("\n" + "="*70)
        print("PRODUCT FAMILY TESTS")
        print("="*70)
        
        # Create family
        family_data = self.make_request(
            "POST",
            "/families",
            json_data={
                "product_id": 845,
                "base_name": "Bose 201 Series",
                "description": "Compact speakers"
            },
            expected_status=201,
            test_name="Create Product Family"
        )
        
        if family_data:
            product_id = family_data.get("product_id")
            
            # Get family
            self.make_request(
                "GET",
                f"/families/{product_id}",
                test_name="Get Product Family"
            )
            
            # List families
            self.make_request(
                "GET",
                "/families?skip=0&limit=10",
                test_name="List Product Families"
            )
            
            # Update family
            self.make_request(
                "PUT",
                f"/families/{product_id}",
                json_data={"base_name": "Bose 201 Series Updated"},
                test_name="Update Product Family"
            )
            
            # Delete family
            self.make_request(
                "DELETE",
                f"/families/{product_id}",
                expected_status=204,
                test_name="Delete Product Family"
            )
    
    # ========================================================================
    # PRODUCT IDENTITY TESTS
    # ========================================================================
    
    def test_product_identities(self):
        """Test product identity endpoints."""
        print("\n" + "="*70)
        print("PRODUCT IDENTITY TESTS")
        print("="*70)
        
        # Create family first
        family_data = self.make_request(
            "POST",
            "/families",
            json_data={
                "product_id": 846,
                "base_name": "Identity Test Family"
            },
            expected_status=201,
            test_name="Create Family (for Identity)"
        )
        
        if family_data:
            product_id = family_data.get("product_id")
            
            # Create Base identity
            identity_data = self.make_request(
                "POST",
                "/identities",
                json_data={
                    "product_id": product_id,
                    "type": "Base",
                    "physical_class": "E"
                },
                expected_status=201,
                test_name="Create Base Identity"
            )
            
            if identity_data:
                identity_id = identity_data.get("id")
                
                # Create Part identity
                self.make_request(
                    "POST",
                    "/identities",
                    json_data={
                        "product_id": product_id,
                        "type": "P",
                        "lci": 1,
                        "physical_class": "C"
                    },
                    expected_status=201,
                    test_name="Create Part Identity"
                )
                
                # Get identity
                self.make_request(
                    "GET",
                    f"/identities/{identity_id}",
                    test_name="Get Product Identity"
                )
                
                # List identities
                self.make_request(
                    "GET",
                    "/identities?skip=0&limit=10",
                    test_name="List Product Identities"
                )
    
    # ========================================================================
    # PRODUCT VARIANT TESTS
    # ========================================================================
    
    def test_product_variants(self):
        """Test product variant endpoints."""
        print("\n" + "="*70)
        print("PRODUCT VARIANT TESTS")
        print("="*70)
        
        # Create family and identity
        family_data = self.make_request(
            "POST",
            "/families",
            json_data={
                "product_id": 847,
                "base_name": "Variant Test Family"
            },
            expected_status=201,
            test_name="Create Family (for Variant)"
        )
        
        if family_data:
            identity_data = self.make_request(
                "POST",
                "/identities",
                json_data={
                    "product_id": family_data.get("product_id"),
                    "type": "Base"
                },
                expected_status=201,
                test_name="Create Identity (for Variant)"
            )
            
            if identity_data:
                identity_id = identity_data.get("id")
                
                # Create variant
                variant_data = self.make_request(
                    "POST",
                    "/variants",
                    json_data={
                        "identity_id": identity_id,
                        "color_code": "BK",
                        "condition_code": "N"
                    },
                    expected_status=201,
                    test_name="Create Product Variant"
                )
                
                if variant_data:
                    variant_id = variant_data.get("id")
                    
                    # Get variant
                    self.make_request(
                        "GET",
                        f"/variants/{variant_id}",
                        test_name="Get Product Variant"
                    )
                    
                    # List variants
                    self.make_request(
                        "GET",
                        "/variants?skip=0&limit=10",
                        test_name="List Product Variants"
                    )
                    
                    # Update variant
                    self.make_request(
                        "PUT",
                        f"/variants/{variant_id}",
                        json_data={"color_code": "SV"},
                        test_name="Update Product Variant"
                    )
    
    # ========================================================================
    # BUNDLE COMPONENT TESTS
    # ========================================================================
    
    def test_bundle_components(self):
        """Test bundle component endpoints."""
        print("\n" + "="*70)
        print("BUNDLE COMPONENT TESTS")
        print("="*70)
        
        # Create parent bundle and child item
        parent_family = self.make_request(
            "POST",
            "/families",
            json_data={
                "product_id": 848,
                "base_name": "Bundle Parent"
            },
            expected_status=201,
            test_name="Create Parent Family"
        )
        
        child_family = self.make_request(
            "POST",
            "/families",
            json_data={
                "product_id": 849,
                "base_name": "Bundle Child"
            },
            expected_status=201,
            test_name="Create Child Family"
        )
        
        if parent_family and child_family:
            parent_identity = self.make_request(
                "POST",
                "/identities",
                json_data={
                    "product_id": parent_family.get("product_id"),
                    "type": "B"
                },
                expected_status=201,
                test_name="Create Parent Identity"
            )
            
            child_identity = self.make_request(
                "POST",
                "/identities",
                json_data={
                    "product_id": child_family.get("product_id"),
                    "type": "Base"
                },
                expected_status=201,
                test_name="Create Child Identity"
            )
            
            if parent_identity and child_identity:
                # Create bundle component
                bundle_data = self.make_request(
                    "POST",
                    "/bundles",
                    json_data={
                        "parent_identity_id": parent_identity.get("id"),
                        "child_identity_id": child_identity.get("id"),
                        "quantity_required": 2,
                        "role": "Primary"
                    },
                    expected_status=201,
                    test_name="Create Bundle Component"
                )
                
                if bundle_data:
                    bundle_id = bundle_data.get("id")
                    
                    # List bundles
                    self.make_request(
                        "GET",
                        "/bundles?skip=0&limit=10",
                        test_name="List Bundle Components"
                    )
    
    # ========================================================================
    # PLATFORM LISTING TESTS
    # ========================================================================
    
    def test_platform_listings(self):
        """Test platform listing endpoints."""
        print("\n" + "="*70)
        print("PLATFORM LISTING TESTS")
        print("="*70)
        
        # Create family, identity, and variant
        family = self.make_request(
            "POST",
            "/families",
            json_data={
                "product_id": 850,
                "base_name": "Listing Test Family"
            },
            expected_status=201,
            test_name="Create Family (for Listing)"
        )
        
        if family:
            identity = self.make_request(
                "POST",
                "/identities",
                json_data={
                    "product_id": family.get("product_id"),
                    "type": "Base"
                },
                expected_status=201,
                test_name="Create Identity (for Listing)"
            )
            
            if identity:
                variant = self.make_request(
                    "POST",
                    "/variants",
                    json_data={
                        "identity_id": identity.get("id"),
                        "color_code": "BK"
                    },
                    expected_status=201,
                    test_name="Create Variant (for Listing)"
                )
                
                if variant:
                    # Create platform listing
                    listing_data = self.make_request(
                        "POST",
                        "/listings",
                        json_data={
                            "variant_id": variant.get("id"),
                            "platform": "AMAZON_US",
                            "external_ref_id": "ASIN123456",
                            "listing_price": 99.99
                        },
                        expected_status=201,
                        test_name="Create Platform Listing"
                    )
                    
                    if listing_data:
                        listing_id = listing_data.get("id")
                        
                        # List listings
                        self.make_request(
                            "GET",
                            "/listings?skip=0&limit=10",
                            test_name="List Platform Listings"
                        )
    
    # ========================================================================
    # INVENTORY TESTS
    # ========================================================================
    
    def test_inventory_items(self):
        """Test inventory item endpoints."""
        print("\n" + "="*70)
        print("INVENTORY ITEM TESTS")
        print("="*70)
        
        # Create family, identity, and variant
        family = self.make_request(
            "POST",
            "/families",
            json_data={
                "product_id": 851,
                "base_name": "Inventory Test Family"
            },
            expected_status=201,
            test_name="Create Family (for Inventory)"
        )
        
        if family:
            identity = self.make_request(
                "POST",
                "/identities",
                json_data={
                    "product_id": family.get("product_id"),
                    "type": "Base"
                },
                expected_status=201,
                test_name="Create Identity (for Inventory)"
            )
            
            if identity:
                variant = self.make_request(
                    "POST",
                    "/variants",
                    json_data={
                        "identity_id": identity.get("id")
                    },
                    expected_status=201,
                    test_name="Create Variant (for Inventory)"
                )
                
                if variant:
                    # Create inventory item
                    item_data = self.make_request(
                        "POST",
                        "/inventory",
                        json_data={
                            "variant_id": variant.get("id"),
                            "serial_number": "SN123456789",
                            "status": "AVAILABLE",
                            "location_code": "A1-S2",
                            "cost_basis": 45.50
                        },
                        expected_status=201,
                        test_name="Create Inventory Item"
                    )
                    
                    if item_data:
                        item_id = item_data.get("id")
                        
                        # List inventory
                        self.make_request(
                            "GET",
                            "/inventory?skip=0&limit=10",
                            test_name="List Inventory Items"
                        )
                        
                        # Update inventory
                        self.make_request(
                            "PUT",
                            f"/inventory/{item_id}",
                            json_data={"status": "SOLD"},
                            test_name="Update Inventory Item"
                        )
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")
        errors = sum(1 for r in self.results if r["status"] == "ERROR")
        
        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Errors: {errors}")
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        print(f"\nPass Rate: {pass_rate:.1f}%")
        
        if failed > 0 or errors > 0:
            print("\nFailed/Error Tests:")
            for result in self.results:
                if result["status"] != "PASS":
                    print(f"  - {result['test']}: {result['details']}")
    
    def run_all_tests(self):
        """Run all test suites."""
        print("\n" + "="*70)
        print("USAV INVENTORY API - COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        self.test_authentication()
        self.test_product_families()
        self.test_product_identities()
        self.test_product_variants()
        self.test_bundle_components()
        self.test_platform_listings()
        self.test_inventory_items()
        
        self.print_summary()


def main():
    """Main entry point."""
    tester = APITester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTest suite interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.client.close()


if __name__ == "__main__":
    main()
