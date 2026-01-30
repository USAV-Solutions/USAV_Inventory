# USAV Inventory System - Deployment Guide

## System Status ✅

All services are running successfully with the updated port configuration:

| Service | Port | Status | URL |
|---------|------|--------|-----|
| Frontend | 3636 | ✅ Healthy | http://localhost:3636 |
| Backend API | 8080 | ✅ Healthy | http://localhost:8080 |
| Database | 5432 | ✅ Healthy | localhost:5432 |
| pgAdmin | 5050 | Available (optional) | http://localhost:5050 |

---

## Port Configuration Summary

### Previous Configuration (Before Update)
- Backend: port 8000
- Frontend: port 3000

### Current Configuration (After Update)
- Backend: port 8080 ✅
- Frontend: port 3636 ✅
- Database: port 5432 (unchanged)

### Files Updated for Port Changes
1. **docker-compose.yml**
   - Backend port mapping: `8080:8080`
   - Backend-dev port mapping: `8080:8080`
   - Backend healthcheck: `http://localhost:8080/health`
   - Frontend port mapping: `3636:3636`
   - Frontend-dev port mapping: `3636:3636`
   - Frontend-dev Vite command: includes `--port 3636`

2. **Backend/Dockerfile**
   - EXPOSE: 8080
   - Healthcheck: `curl -f http://localhost:8080/health`
   - CMD: uvicorn with `--port 8080`

3. **frontend/Dockerfile**
   - EXPOSE: 3636
   - Healthcheck: `wget --quiet --spider http://localhost:3636`
   - CMD: serve with `-l 3636`

4. **frontend/Dockerfile.dev**
   - EXPOSE: 3636
   - CMD: npm run dev with `--port 3636`

5. **frontend/vite.config.ts**
   - server.port: 3636
   - proxy target: `http://backend:8080`

---

## Quick Start

### Start All Services
```bash
# Navigate to the project root
cd c:\myspace\USAV\database_creation\USAV_Inventory

# Start all services (database, backend, frontend, backup)
docker-compose up -d
```

### Run Database Migrations (First Time Only)
```bash
# Apply migrations
docker-compose --profile migrate up migrations
```

### Development Mode (with Hot Reload)
```bash
# Start database + dev backend + dev frontend
docker-compose --profile dev up -d

# This enables:
# - Backend hot reload (code changes auto-restart)
# - Frontend hot reload (Vite HMR)
```

### Stop All Services
```bash
docker-compose down
```

---

## Access Points

### Application
- **Frontend**: http://localhost:3636
- **Backend Health**: http://localhost:8080/health

### API Documentation
- **Swagger UI**: http://localhost:8080/api/v1/docs
- **ReDoc**: http://localhost:8080/api/v1/redoc

### Database Management (Optional)
```bash
# Enable pgAdmin
docker-compose --profile tools up -d

# Access pgAdmin
# URL: http://localhost:5050
# Email: admin@example.com (default)
# Password: admin (default)
```

---

## Environment Configuration

Create a `.env` file in the project root for custom configuration:

```env
# Database Configuration
DB_USER=postgres
DB_PASS=devpassword123
DB_NAME=inventory_system

# Zoho Integration (optional)
ZOHO_CLIENT_ID=
ZOHO_CLIENT_SECRET=
ZOHO_REFRESH_TOKEN=
ZOHO_ORGANIZATION_ID=

# pgAdmin Configuration (optional)
PGADMIN_EMAIL=it@usavshop.com
PGADMIN_PASSWORD=admin
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs backend    # Backend logs
docker-compose logs frontend   # Frontend logs
docker-compose logs db         # Database logs

# Rebuild images (if code changed)
docker-compose build --no-cache

# Full restart
docker-compose down && docker-compose up -d
```

### Port Already in Use
If a port is already in use, either:
1. Stop the service using that port
2. Change the port mapping in `docker-compose.yml`

Example to use different ports:
```yaml
services:
  backend:
    ports:
      - "8081:8080"  # Host:Container
```

### Database Connection Issues
```bash
# Check database health
docker-compose logs db

# Verify database is running
docker ps | grep usav_db

# Reset database (WARNING: deletes all data)
docker-compose down -v  # -v removes volumes
docker-compose up -d
```

### Frontend Can't Connect to Backend
- Verify backend is running: http://localhost:8080/health
- Check CORS configuration in `Backend/app/core/config.py`
- Ensure frontend is trying to connect to port 8080 (check vite.config.ts proxy)

---

## Implementation Changes

### Database Changes
- Added 4 new lookup tables (Brand, Color, Condition, LCIDefinition)
- Updated ProductFamily with new fields (brand, dimensions, weight, kit products)
- Changed IdentityType enum (Base → Product)

### Backend API Changes
- Added CRUD endpoints for all lookup tables
- Created new schemas and repository layer
- All endpoints under `/api/v1/` prefix

### Frontend UI Changes
- Created unified InventoryManagement page
- Replaced ProductIdentities and VariantManager pages
- New CreateProductDialog with type-specific fields
- Added search, filtering, and grouped view functionality

### Docker/Deployment Changes
- Updated all port configurations (8000→8080, 3000→3636)
- Fixed healthcheck endpoints
- Updated all service startup commands
- Added proper port exposure in all Dockerfiles

---

## Monitoring & Debugging

### View Real-Time Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db

# Last 50 lines
docker-compose logs --tail=50
```

### Check Container Status
```bash
# Show all containers
docker-compose ps

# Show detailed info
docker inspect usav_backend
```

### Execute Commands in Container
```bash
# Access backend shell
docker exec -it usav_backend /bin/bash

# Access database
docker exec -it usav_db psql -U postgres -d inventory_system
```

---

## Documentation Files

- **IMPLEMENTATION_CHANGELOG.md** - Detailed list of all changes made
- **DEPLOYMENT_GUIDE.md** - This file
- **API_ISSUES_TO_FIX.md** - Known issues and fixes
- **FRONTEND_API_ENDPOINTS.md** - Frontend API endpoint documentation

---

## Next Steps

1. **Verify Application**: Open http://localhost:3636 in browser
2. **Run Migrations**: `docker-compose --profile migrate up migrations`
3. **Test API**: Visit http://localhost:8080/api/v1/docs
4. **Check Database**: Verify data in database

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs backend`
2. Review IMPLEMENTATION_CHANGELOG.md for recent changes
3. Verify port configuration in docker-compose.yml
4. Ensure Docker daemon is running

---

**Last Updated**: January 29, 2026
**System Version**: v1.0.0
**Frontend Port**: 3636
**Backend Port**: 8080
