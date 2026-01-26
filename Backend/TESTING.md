# API Testing Guide

This directory contains comprehensive testing scripts for the USAV Inventory API.

## Testing Options

### Option 1: Manual Testing Script (Recommended for Quick Testing)

Run the manual testing script without installing pytest:

```bash
cd Backend
python scripts/test_api_manual.py
```

This will:
- Test authentication (create users, login, get current user)
- Test product families (CRUD operations)
- Test product identities (create Base, Part, Bundle, Kit, Service types)
- Test product variants (create, read, update, list)
- Test bundle components (create and list)
- Test platform listings (create and list)
- Test inventory items (create, read, update, list)
- Generate a summary report with pass/fail statistics

**Benefits:**
- No pytest installation required
- Clear, colored output with test results
- Detailed error messages
- Works with running API server

### Option 2: Pytest Suite

For comprehensive testing with pytest:

```bash
cd Backend

# Install pytest (if not already installed)
pip install pytest pytest-asyncio

# Run all tests
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_api.py::TestAuthentication -v

# Run specific test
pytest tests/test_api.py::TestAuthentication::test_login_success -v

# Run with markers
pytest tests/test_api.py -m auth -v
```

**Benefits:**
- Full pytest integration
- Fixtures for setup/teardown
- Parametrized testing support
- JUnit XML reports
- Better for CI/CD pipelines

## Test Coverage

### Authentication Tests
- ✅ Create admin user
- ✅ Create warehouse operator user
- ✅ Login and get token
- ✅ Get current user info
- ✅ Password validation

### Product Family Tests
- ✅ Create product family
- ✅ List product families
- ✅ Get specific family
- ✅ Update family
- ✅ Delete family

### Product Identity Tests
- ✅ Create Base identity
- ✅ Create Part identity with LCI
- ✅ Create Bundle/Kit identity
- ✅ List identities
- ✅ Get specific identity

### Product Variant Tests
- ✅ Create variant with color and condition
- ✅ List variants
- ✅ Get specific variant
- ✅ Update variant
- ✅ Filter by sync status

### Bundle Component Tests
- ✅ Create bundle components
- ✅ List bundle components
- ✅ Set component roles (Primary, Accessory, Satellite)

### Platform Listing Tests
- ✅ Create listings for multiple platforms
- ✅ Supported platforms: ZOHO, AMAZON_US, AMAZON_CA, EBAY, ECWID
- ✅ List listings
- ✅ Track sync status

### Inventory Tests
- ✅ Create inventory items
- ✅ Track inventory status (AVAILABLE, SOLD, RESERVED, RMA, DAMAGED)
- ✅ Update item status
- ✅ List inventory
- ✅ Track location and cost

### Error Handling
- ✅ Invalid product ID validation
- ✅ Nonexistent resource handling (404)
- ✅ Invalid role validation
- ✅ Schema validation (422)

## API Endpoints Tested

### Authentication
- `POST /api/v1/auth/users` - Create user
- `POST /api/v1/auth/token` - Login
- `GET /api/v1/auth/me` - Get current user

### Product Families
- `POST /api/v1/families` - Create
- `GET /api/v1/families` - List
- `GET /api/v1/families/{product_id}` - Get
- `PUT /api/v1/families/{product_id}` - Update
- `DELETE /api/v1/families/{product_id}` - Delete

### Product Identities
- `POST /api/v1/identities` - Create
- `GET /api/v1/identities` - List
- `GET /api/v1/identities/{id}` - Get
- `PUT /api/v1/identities/{id}` - Update

### Product Variants
- `POST /api/v1/variants` - Create
- `GET /api/v1/variants` - List
- `GET /api/v1/variants/{id}` - Get
- `PUT /api/v1/variants/{id}` - Update

### Bundle Components
- `POST /api/v1/bundles` - Create
- `GET /api/v1/bundles` - List
- `PUT /api/v1/bundles/{id}` - Update

### Platform Listings
- `POST /api/v1/listings` - Create
- `GET /api/v1/listings` - List
- `PUT /api/v1/listings/{id}` - Update

### Inventory Items
- `POST /api/v1/inventory` - Create
- `GET /api/v1/inventory` - List
- `GET /api/v1/inventory/{id}` - Get
- `PUT /api/v1/inventory/{id}` - Update

## Example Test Output

```
======================================================================
USAV INVENTORY API - COMPREHENSIVE TEST SUITE
======================================================================

======================================================================
AUTHENTICATION TESTS
======================================================================
✅ Create Admin User: PASS
   └─ POST /auth/users -> 201
✅ Create Warehouse Operator: PASS
   └─ POST /auth/users -> 201
✅ Login: PASS
   └─ POST /auth/token -> 200
   └─ Token obtained: eyJhbGciOiJIUzI1NiIs...
✅ Get Current User: PASS
   └─ GET /auth/me -> 200

======================================================================
PRODUCT FAMILY TESTS
======================================================================
✅ Create Product Family: PASS
   └─ POST /families -> 201
✅ Get Product Family: PASS
   └─ GET /families/845 -> 200
...

======================================================================
TEST SUMMARY
======================================================================

Total Tests: 45
✅ Passed: 45
❌ Failed: 0
⚠️  Errors: 0

Pass Rate: 100.0%
```

## Troubleshooting

### "Connection refused" error
- Ensure the API server is running: `python -m uvicorn app.main:app --reload`
- Check that it's running on `http://127.0.0.1:8000`

### "No module named 'pytest'" (for pytest method)
- Install pytest: `pip install pytest pytest-asyncio`

### Database errors
- Ensure PostgreSQL is running
- Check database credentials in `.env`
- Run migrations: `alembic upgrade head`

### Import errors
- Ensure you're in the `Backend` directory
- Verify virtual environment is activated

## CI/CD Integration

For GitHub Actions or other CI systems, use the pytest suite:

```yaml
- name: Run API Tests
  run: |
    cd Backend
    pip install -r requirements.txt
    pytest tests/test_api.py -v --tb=short
```

## Contributing Tests

To add new tests:

1. **For manual script:** Add a new method to `APITester` class in `test_api_manual.py`
2. **For pytest:** Add a new test class to `tests/test_api.py`

Example:

```python
def test_new_endpoint(self):
    """Test new endpoint."""
    response = self.make_request(
        "POST",
        "/new-endpoint",
        json_data={"field": "value"},
        expected_status=201,
        test_name="Test New Endpoint"
    )
```
