# USAV Core Inventory Database

Production-ready PostgreSQL database and FastAPI backend for managing USAV product inventory, implementing the **Hub & Spoke Middleware Architecture**.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    USAV Inventory Hub                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   FastAPI   │  │  PostgreSQL │  │     Alembic Migrations  │  │
│  │   Backend   │◄─┤   Database  │◄─┤                         │  │
│  └──────┬──────┘  └─────────────┘  └─────────────────────────┘  │
│         │                                                        │
└─────────┼────────────────────────────────────────────────────────┘
          │
          ▼ Push Updates
    ┌─────┴─────┐
    │   Spokes  │
    ├───────────┤
    │  • Zoho   │
    │  • Amazon │
    │  • eBay   │
    │  • Ecwid  │
    └───────────┘
```

## 📁 Project Structure

```
USAV_Database_Construct/
├── docker-compose.yml          # Container orchestration
├── .env                        # Environment variables (create from .env.example)
├── database_documentation.md   # Detailed schema documentation
├── database_erd.mmd           # Entity Relationship Diagram (Mermaid)
│
└── Backend/
    ├── Dockerfile             # Production container build
    ├── requirements.txt       # Python dependencies
    ├── alembic.ini           # Alembic configuration
    ├── .env.example          # Environment template
    │
    ├── app/
    │   ├── main.py           # FastAPI application entry
    │   ├── __init__.py
    │   │
    │   ├── core/
    │   │   ├── config.py     # Pydantic settings (DB + JWT)
    │   │   ├── database.py   # Async SQLAlchemy setup
    │   │   └── security.py   # JWT & password hashing utilities
    │   │
    │   ├── models/
    │   │   ├── entities.py   # SQLAlchemy ORM models (Product/Inventory)
    │   │   ├── user.py       # User model with RBAC
    │   │   └── __init__.py   # Model exports
    │   │
    │   ├── schemas/
    │   │   ├── auth.py       # Authentication schemas
    │   │   └── __init__.py   # Pydantic schemas
    │   │
    │   ├── repositories/
    │   │   ├── base.py       # Generic CRUD operations
    │   │   ├── product.py    # Product-related repos
    │   │   ├── inventory.py  # Inventory-related repos
    │   │   ├── user.py       # User authentication repo
    │   │   └── __init__.py   # Repository exports
    │   │
    │   ├── api/
    │       ├── __init__.py   # API router aggregation
    │       ├── deps.py       # Auth dependencies & role guards
    │       │
    │       └── routes/       # Endpoint handlers
    │           ├── auth.py           # Authentication endpoints
    │           ├── families.py
    │           ├── identities.py
    │           ├── variants.py
    │           ├── bundles.py
    │           ├── listings.py
    │           ├── inventory.py
    │           └── __init__.py       # Router exports
    │
    └── migrations/
        ├── env.py            # Alembic environment
        ├── script.py.mako    # Migration template
        └── versions/         # Migration scripts
            ├── 0001_initial_schema.py   # Product/inventory tables
            └── 0002_add_users.py        # Users table with RBAC
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- (Optional) Python 3.12+ for local development

### 1. Clone and Configure

```bash
cd USAV_Database_Construct

# Create environment file
cp .env.example .env
# Edit .env with your settings (especially DB_PASS for production!)
```

### 2. Start Services

```bash
# Start database and backend (production mode)
docker-compose up -d

# Or start with development mode (hot reload)
docker-compose --profile dev up -d backend-dev

# Run database migrations
docker-compose --profile migrate run --rm migrations

# (Optional) Start pgAdmin for database management
docker-compose --profile tools up -d pgadmin
```

### 3. Access the API

- **API Documentation**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health
- **pgAdmin** (if enabled): http://localhost:5050

## 📊 Database Schema

The database implements the **Two-Layer Identification Model**:

### Layer 1: Product Identity (Engineering Layer)
- **Immutable** after creation
- Generates UPIS-H (Unique Product Identity Signature - Human Readable)
- Example: `00845-P-1` (Product 845, Part 1)

### Layer 2: Product Variant (Sales Layer)
- Defines sellable configurations (Color, Condition)
- Generates full SKU
- Example: `00845-P-1-WY-N` (White, New)

### Tables

| Table | Purpose |
|-------|---------|
| `product_family` | High-level product grouping (5-digit ECWID ID) |
| `product_identity` | Engineering identity (UPIS-H + hex signature) |
| `product_variant` | Sellable configurations (SKU + Zoho sync) |
| `bundle_component` | Bill of Materials for bundles/kits |
| `platform_listing` | External platform sync (Amazon, eBay, etc.) |
| `inventory_item` | Physical inventory tracking |

## 🔌 API Endpoints

### Product Families
```
GET    /api/v1/families           # List all families
POST   /api/v1/families           # Create family
GET    /api/v1/families/{id}      # Get with identities
PATCH  /api/v1/families/{id}      # Update
DELETE /api/v1/families/{id}      # Delete
```

### Product Identities
```
GET    /api/v1/identities                  # List identities
POST   /api/v1/identities                  # Create (auto-generates UPIS-H)
GET    /api/v1/identities/{id}             # Get with variants
GET    /api/v1/identities/upis/{upis_h}    # Get by UPIS-H
```

### Product Variants
```
GET    /api/v1/variants                    # List variants
POST   /api/v1/variants                    # Create (auto-generates SKU)
GET    /api/v1/variants/{id}               # Get with listings
GET    /api/v1/variants/sku/{full_sku}     # Get by SKU
GET    /api/v1/variants/pending-sync/zoho  # Get pending Zoho sync
```

### Inventory
```
GET    /api/v1/inventory                   # List items
POST   /api/v1/inventory                   # Create item
POST   /api/v1/inventory/{id}/reserve      # Reserve item
POST   /api/v1/inventory/{id}/sell         # Mark as sold
GET    /api/v1/inventory/summary/{variant_id}  # Count by status
GET    /api/v1/inventory/value/total       # Total inventory value
```

### Bundle Components
```
GET    /api/v1/bundles                     # List components
POST   /api/v1/bundles                     # Add component to bundle
GET    /api/v1/bundles/parent/{id}/components  # Get BOM
GET    /api/v1/bundles/child/{id}/bundles  # Find containing bundles
```

### Platform Listings
```
GET    /api/v1/listings                    # List listings
POST   /api/v1/listings                    # Create listing
GET    /api/v1/listings/pending            # Get pending sync
GET    /api/v1/listings/errors             # Get failed sync
POST   /api/v1/listings/{id}/mark-synced   # Mark as synced
POST   /api/v1/listings/{id}/mark-error    # Mark as error
```

## � Authentication & Authorization

The API uses **OAuth2 Password Flow** with JWT tokens and **Role-Based Access Control (RBAC)**.

**Important**: No self-registration. All users are created by administrators who assign roles.

### Supported Roles

| Role | Permissions |
|------|-----------|
| `ADMIN` | Full access - user management, all data operations |
| `WAREHOUSE_OP` | Inventory operations - receive, move, reserve stock |
| `SALES_REP` | Read-only product data, create orders, view inventory |
| `SYSTEM_BOT` | API integrations, automated sync operations |

### Authentication Endpoints

```
POST   /api/v1/auth/token              # Login (OAuth2 password flow)
GET    /api/v1/auth/me                 # Get current user info
POST   /api/v1/auth/me/change-password # Change password
```

### User Management (Admin Only)

```
GET    /api/v1/auth/users              # List all users
POST   /api/v1/auth/users              # Create user (admin assigns role)
GET    /api/v1/auth/users/{id}         # Get user details
PATCH  /api/v1/auth/users/{id}         # Update user
DELETE /api/v1/auth/users/{id}         # Delete user
```

**Create User Example** (Admin only - no self-registration):
```bash
curl -X POST http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_warehouse",
    "password": "secure_password_123",
    "full_name": "John Smith",
    "role": "WAREHOUSE_OP",
    "is_active": true
  }'
```

### Using Authentication

1. **Login** to get JWT token:
```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=your_password"
```

2. **Use token** in subsequent requests:
```bash
curl http://localhost:8000/api/v1/families \
  -H "Authorization: Bearer <your_token>"
```

3. **In code** with dependency injection:
```python
from app.api.deps import require_admin

@router.post("/", dependencies=[Depends(require_admin)])
async def admin_only_endpoint():
    # Only ADMIN users can access
    pass
```

## �🔧 Development

### Local Development (without Docker)

```bash
cd Backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DB_HOST=localhost
export DB_PASS=your_password
export SECRET_KEY=$(openssl rand -hex 32)  # Generate secure key

# Run migrations
alembic upgrade head

# Create admin user (optional - via API or direct DB insert)
# Default test user: admin / admin_password

# Start development server
uvicorn app.main:app --reload
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
docker-compose --profile migrate run --rm migrations \
    alembic revision --autogenerate -m "description"

# Or manually
docker-compose --profile migrate run --rm migrations \
    alembic revision -m "description"

# Apply migrations
docker-compose --profile migrate run --rm migrations \
    alembic upgrade head
```

### Running Tests

```bash
# In Docker
docker-compose exec backend pytest

# Local
pytest
```

## 🔐 Production Considerations

1. **Change default passwords** in `.env`
2. **Generate strong SECRET_KEY**: `openssl rand -hex 32`
3. **Enable HTTPS** via reverse proxy (nginx/traefik)
4. **Configure CORS origins** for your domains
5. **Set up monitoring** (Prometheus, Grafana)
6. **Review backup schedule** in docker-compose.yml
7. **Consider read replicas** for scaling
8. **Rotate JWT secret** periodically for enhanced security

## 📝 License

Proprietary - USAV Internal Use Only
