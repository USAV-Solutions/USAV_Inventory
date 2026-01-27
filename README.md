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

## ✨ Core Features

### 1. **Two-Layer Product Identification**
   - **UPIS-H (Unique Product Identity Signature)**: Immutable engineering identifier
   - **Full SKU**: Dynamic sales identifier with variant attributes (color, condition, size)
   - Automatic generation and validation for data integrity

### 2. **Comprehensive Inventory Management**
   - Real-time stock tracking with multiple status types
   - Inventory reservations and sales workflows
   - Inventory value calculations and reporting
   - Batch operations for efficient warehouse operations

### 3. **Platform Integration (Hub & Spoke)**
   - Multi-platform synchronization (Zoho, Amazon, eBay, Ecwid)
   - Pending sync tracking and error handling
   - Automatic status updates across platforms
   - Configurable sync schedules and rules

### 4. **Bundle & Kit Management**
   - Define products as bundles of multiple components
   - Automatic BOM (Bill of Materials) generation
   - Track parent-child relationships
   - Support for complex product hierarchies

### 5. **Role-Based Access Control (RBAC)**
   - Four permission levels: ADMIN, WAREHOUSE_OP, SALES_REP, SYSTEM_BOT
   - Admin-controlled user management (no self-registration)
   - JWT-based authentication with secure password hashing
   - Fine-grained endpoint access control

### 6. **Database Migrations & Version Control**
   - Alembic-based migration system
   - Track schema changes over time
   - Automatic migration deployment in Docker
   - Rollback capability for production safety

### 7. **Automated Backups**
   - Daily database backups (configurable schedule)
   - 7-day daily, 4-week weekly, 6-month monthly retention
   - Persistent backup storage in local filesystem
   - Easy restore capability

### 8. **API Documentation**
   - Interactive OpenAPI/Swagger documentation
   - ReDoc alternative documentation view
   - Auto-generated from code with Pydantic schemas
   - Built-in request/response examples

### 9. **Production-Ready Architecture**
   - Async/await with asyncio and asyncpg
   - Connection pooling for database efficiency
   - Health checks for all services
   - Docker-based containerization

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (v1.29+)
- (Optional) Python 3.12+ for local development

### 1. Clone and Configure

```bash
cd USAV_Inventory

# Create environment file from template
cp Backend/.env.example .env
# Edit .env with your settings (especially DB_PASS for production!)
```

### 2. Access the Application

- **API Documentation**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health
- **pgAdmin** (optional): http://localhost:5050

## 🐳 Docker Deployment Guide

### Environment Configuration

Create a `.env` file in the root directory with the following variables:

```env
# Database Configuration
DB_USER=postgres
DB_PASS=your_secure_password_123
DB_NAME=inventory_system

# Environment Type (development/staging/production)
ENVIRONMENT=development
DEBUG=false

# Zoho Integration (optional)
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_REFRESH_TOKEN=your_refresh_token
ZOHO_ORGANIZATION_ID=your_org_id

# pgAdmin (optional)
PGADMIN_EMAIL=it@usavshop.local
PGADMIN_PASSWORD=admin_password
```

### Production Deployment (Full Stack)

**Start all services** (database, backend, frontend, backups):

```bash
docker-compose up -d
```

This starts:
- ✅ PostgreSQL database (port 5432)
- ✅ FastAPI backend (port 8000)
- ✅ React frontend (port 3000)
- ✅ Automated daily backups
- ✅ Network connectivity between services

**Initialize the database** (run once):

```bash
docker-compose --profile migrate run --rm migrations
```

This executes Alembic migrations to create tables and schema.

**Verify services are running**:

```bash
docker-compose ps
```

Expected output:
```
NAME                COMMAND                STATUS
usav_db             postgres               Up (healthy)
usav_backend        uvicorn app.main:app   Up (healthy)
usav_frontend       npm run build           Up (healthy)
usav_backup         postgres-backup        Up
```

### Development Deployment (Hot Reload)

**Start with development profiles** (auto-reloading backend & frontend):

```bash
docker-compose --profile dev up -d
```

This starts:
- ✅ PostgreSQL database
- ✅ FastAPI backend (with hot reload on code changes)
- ✅ React frontend (with hot reload on code changes)
- ✅ Volume mounts for live code editing

**Edit code directly** in your IDE and changes reflect immediately in containers.

### Database Management (Optional)

**Start pgAdmin UI** for visual database management:

```bash
docker-compose --profile tools up -d pgadmin
```

Then visit http://localhost:5050
- Email: it@usavshop.com (configured in .env)
- Password: admin_password (configured in .env)

**Connect to PostgreSQL from pgAdmin**:
1. In pgAdmin, click "Register" → "Server"
2. Name: "USAV Database"
3. Connection tab → Hostname: `db`, Username: `postgres`, Password: `your_db_password`
4. Save

### Service-Specific Commands

**Start only database and backend** (no frontend):
```bash
docker-compose up -d db backend
```

**View real-time logs** from all services:
```bash
docker-compose logs -f
```

**View logs from specific service**:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

**Execute command inside container**:
```bash
# Access backend shell
docker-compose exec backend bash

# Access database CLI
docker-compose exec db psql -U postgres -d inventory_system
```

**Run database migrations manually**:
```bash
# Auto-generate migration from model changes
docker-compose --profile migrate run --rm migrations \
    alembic revision --autogenerate -m "Add new column"

# Apply latest migrations
docker-compose --profile migrate run --rm migrations \
    alembic upgrade head

# Rollback to previous migration
docker-compose --profile migrate run --rm migrations \
    alembic downgrade -1
```

**Stop all services**:
```bash
docker-compose down
```

**Stop and remove all data** (careful!):
```bash
docker-compose down -v
```

**Restart a specific service**:
```bash
docker-compose restart backend
```

### Backup Management

**Manual backup** (in addition to automated daily backups):
```bash
docker-compose exec db-backup backup
```

**Restore from backup**:
```bash
# List available backups
ls backups/

# Restore specific backup
docker-compose exec db pg_restore -U postgres -d inventory_system /backups/<backup_file>
```

**View automated backup settings** in `docker-compose.yml`:
- Daily schedule: `@daily` (customizable to `@hourly`, `@weekly`, etc.)
- Retention: 7 days daily, 4 weeks weekly, 6 months monthly

## 🎯 Complete Project Stack

### Backend (FastAPI)
Located in [Backend/](Backend/) directory:
- **Framework**: FastAPI with async SQLAlchemy
- **Database**: PostgreSQL with async drivers
- **Authentication**: JWT tokens with RBAC
- **API Docs**: Auto-generated OpenAPI/Swagger & ReDoc
- **Port**: 8000

### Frontend (React + TypeScript)
Located in [frontend/](frontend/) directory:
- **Framework**: React with Vite build tool
- **Language**: TypeScript for type safety
- **Build**: Docker-optimized production builds
- **Port**: 3000

### Database (PostgreSQL)
- **Version**: PostgreSQL 16 Alpine (lightweight)
- **Port**: 5432
- **Schema**: Fully managed via Alembic migrations
- **Backup**: Automated daily backups with configurable retention

### Supporting Services
- **Alembic**: Database migration management
- **pgAdmin**: Optional web UI for database management
- **Backup Service**: Automated daily database backups with retention policies
- **Docker Compose**: Orchestrates all containers and networking

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

### Using Docker (Recommended)

```bash
# Start with live code reload
docker-compose --profile dev up -d

# Watch logs
docker-compose logs -f

# Access backend shell
docker-compose exec backend bash

# Run tests in container
docker-compose exec backend pytest

# Execute database commands
docker-compose exec db psql -U postgres -d inventory_system
```

### Local Development (Without Docker)

#### Backend Setup

```bash
cd Backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
set DB_HOST=localhost
set DB_PASS=your_password
set DB_USER=postgres
set DB_NAME=inventory_system
set SECRET_KEY=your_secret_key_here

# Run migrations (requires PostgreSQL running separately)
alembic upgrade head

# Start development server (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at http://localhost:8000/api/v1/docs

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server (with hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Frontend will be available at http://localhost:5173 (Vite default port)

### Database Migrations

**Auto-generate migration** from model changes:
```bash
# In Docker
docker-compose --profile migrate run --rm migrations \
    alembic revision --autogenerate -m "Add user table"

# Locally
alembic revision --autogenerate -m "Add user table"
```

**Apply migrations**:
```bash
# In Docker
docker-compose --profile migrate run --rm migrations alembic upgrade head

# Locally
alembic upgrade head
```

**Rollback migrations**:
```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade ae1027a6acf
```

**View migration history**:
```bash
alembic current
alembic history
```

### Testing

**Run all tests** in Docker:
```bash
docker-compose exec backend pytest
```

**Run specific test file**:
```bash
docker-compose exec backend pytest tests/test_auth.py
```

**Run with coverage**:
```bash
docker-compose exec backend pytest --cov=app tests/
```

**Local testing** (requires local environment setup):
```bash
pytest
pytest -v  # Verbose output
pytest --cov=app  # With coverage
```

## 🔐 Production Considerations

### Security Checklist

- [ ] **Change all default passwords** in `.env` - use strong, unique passwords
- [ ] **Generate strong SECRET_KEY**: 
  ```bash
  openssl rand -hex 32
  ```
- [ ] **Enable HTTPS** via reverse proxy (nginx/traefik) - never expose HTTP in production
- [ ] **Configure CORS origins** for your specific domains (update in Backend/.env)
- [ ] **Set up secrets management** - use environment variables or secrets manager
- [ ] **Rotate JWT secret** periodically for enhanced security
- [ ] **Enable database backups** - verify backup process works (test restore)
- [ ] **Configure health checks** - monitor all service health endpoints

### Performance & Scaling

- [ ] **Review backup schedule** in docker-compose.yml (currently daily)
- [ ] **Set up monitoring** (Prometheus, Grafana, or similar)
- [ ] **Configure logging** - centralize logs (ELK stack, CloudWatch, etc.)
- [ ] **Consider read replicas** for scaling database reads
- [ ] **Implement caching** - Redis for frequent queries
- [ ] **Use CDN** for static frontend assets
- [ ] **Configure rate limiting** on API endpoints
- [ ] **Set up alerts** for service failures and resource exhaustion

### Deployment Best Practices

```bash
# Use production environment settings
ENVIRONMENT=production
DEBUG=false

# Use strong database password (at least 16 characters)
DB_PASS=your_very_secure_password_with_special_chars_123!@#

# Disable unnecessary profiles (dev, tools)
docker-compose -f docker-compose.yml up -d

# Verify all services are healthy
docker-compose ps

# Check logs for any errors
docker-compose logs

# Set resource limits in docker-compose.yml for stability
# - Memory limits
# - CPU limits
# - Restart policies
```

## 📚 Additional Documentation

- [Database Documentation](database_documentation_v1.0.md) - Detailed schema, entities, and relationships
- [Database ERD](database_erd.mmd) - Visual entity relationship diagram
- [Backend Testing Guide](Backend/TESTING.md) - Test structure and examples
- [Frontend README](frontend/README.md) - Frontend-specific setup and development
- [Docker Guide](DOCKER_GUIDE.md) - Detailed Docker troubleshooting

## 📝 License

Proprietary - USAV Internal Use Only
