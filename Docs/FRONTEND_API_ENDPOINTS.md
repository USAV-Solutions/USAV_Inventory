# USAV Inventory Frontend - API Endpoints Documentation

This document lists all API endpoints used by the React frontend application.

## Base URL
```
http://backend:8000/api/v1
```

> **Note**: In development mode with Docker, the frontend uses `http://backend:8000` through the Docker network.
> In production or local development, this would be `http://localhost:8000` or the appropriate backend URL.

---

## Authentication Endpoints

### Login
**Endpoint:** `POST /api/v1/auth/token`  
**Content-Type:** `application/x-www-form-urlencoded`  
**Request Body:**
```
username=<username>&password=<password>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Used By:** `src/hooks/useAuth.tsx` - `login()` function  
**Page:** Login page  
**Authentication:** None (public endpoint)

---

## Product Identity Endpoints

### List Product Identities
**Endpoint:** `GET /api/v1/identities`  
**Query Parameters:**
- `skip` (optional, default: 0): Number of records to skip for pagination
- `limit` (optional, default: 100): Number of records to return
- `product_id` (optional): Filter by product family ID

**Response:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 100,
  "items": [
    {
      "id": 1,
      "product_id": 845,
      "type": "P",
      "lci": 1,
      "upis_h": "000845-P-001",
      "hex_signature": "abcd1234",
      "created_at": "2026-01-20T10:30:00Z"
    }
  ]
}
```

**Used By:** `src/pages/ProductIdentities.tsx`  
**Page:** Product Identities  
**Authentication:** Required (Bearer token)

### Create Product Identity
**Endpoint:** `POST /api/v1/identities`  
**Request Body:**
```json
{
  "product_id": 845,
  "type": "P",
  "lci": 1
}
```

**Response:**
```json
{
  "id": 1,
  "product_id": 845,
  "type": "P",
  "lci": 1,
  "upis_h": "000845-P-001",
  "hex_signature": "abcd1234",
  "created_at": "2026-01-20T10:30:00Z"
}
```

**Used By:** `src/pages/ProductIdentities.tsx` - `createMutation`  
**Page:** Product Identities  
**Authentication:** Required (Admin role)

---

## Product Variant Endpoints

### List Product Variants
**Endpoint:** `GET /api/v1/variants`  
**Query Parameters:** None (currently returns all variants)

**Response:**
```json
[
  {
    "id": 1,
    "identity_id": 1,
    "condition": "NEW",
    "price": 29.99,
    "zoho_status": "SYNCED",
    "created_at": "2026-01-20T10:30:00Z"
  }
]
```

**Used By:** `src/pages/VariantManager.tsx`  
**Page:** Variant Manager  
**Authentication:** Required (Bearer token)

### Update Product Variant Price
**Endpoint:** `PATCH /api/v1/variants/{id}`  
**Path Parameters:**
- `id` (required): Variant ID

**Request Body:**
```json
{
  "price": 34.99
}
```

**Response:**
```json
{
  "id": 1,
  "identity_id": 1,
  "condition": "NEW",
  "price": 34.99,
  "zoho_status": "DIRTY",
  "created_at": "2026-01-20T10:30:00Z"
}
```

**Used By:** `src/pages/VariantManager.tsx` - `updateMutation`  
**Page:** Variant Manager  
**Authentication:** Required (Bearer token)

### Create Product Variant
**Endpoint:** `POST /api/v1/variants`  
**Request Body:**
```json
{
  "identity_id": 1,
  "condition": "NEW",
  "price": 29.99
}
```

**Response:**
```json
{
  "id": 1,
  "identity_id": 1,
  "condition": "NEW",
  "price": 29.99,
  "zoho_status": "SYNCED",
  "created_at": "2026-01-20T10:30:00Z"
}
```

**Used By:** `src/pages/VariantManager.tsx` - `createMutation`  
**Page:** Variant Manager  
**Authentication:** Required (Bearer token)

---

## Inventory Endpoints

### Receive Inventory Item
**Endpoint:** `POST /api/v1/inventory/receive`  
**Request Body:**
```json
{
  "serial_number": "SN12345678"
}
```

**Response:** 
```json
{
  "serial_number": "SN12345678",
  "sku": "00845-P-1-WY-N",
  "location_code": "A1-001",
  "status": "IN_STOCK",
  "received_at": "2026-01-27T14:00:00Z"
}
```

**Used By:** `src/pages/WarehouseOps.tsx` - `handleReceive()`  
**Page:** Warehouse Operations  
**Mode:** Receive  
**Authentication:** Required (Warehouse Operator role)

### Move Inventory Item
**Endpoint:** `POST /api/v1/inventory/move`  
**Request Body:**
```json
{
  "serial_number": "SN12345678",
  "new_location": "B2-005"
}
```

**Response:**
```json
{
  "serial_number": "SN12345678",
  "previous_location": "A1-001",
  "new_location": "B2-005",
  "moved_at": "2026-01-27T14:05:00Z"
}
```

**Used By:** `src/pages/WarehouseOps.tsx` - `handleMove()`  
**Page:** Warehouse Operations  
**Mode:** Move  
**Authentication:** Required (Warehouse Operator role)

### Audit Inventory (Get Item Details)
**Endpoint:** `GET /api/v1/inventory/audit/{sku_or_serial}`  
**Path Parameters:**
- `sku_or_serial` (required): SKU or serial number to look up

**Response:**
```json
{
  "items": [
    {
      "serial_number": "SN12345678",
      "location_code": "A1-001",
      "status": "IN_STOCK",
      "received_at": "2026-01-20T10:30:00Z"
    }
  ]
}
```

**Used By:**
- `src/pages/WarehouseOps.tsx` - `handleMove()` and `handleAudit()`
- `src/pages/StockLookup.tsx`

**Page:** Warehouse Operations (Move/Audit modes) and Stock Lookup  
**Authentication:** Required (Bearer token)

---

## Response Codes Summary

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |
| 500 | Server Error |

---

## Authentication

All endpoints except `/api/v1/auth/token` require:
- **Header:** `Authorization: Bearer <access_token>`
- The token is obtained from the login endpoint
- Token is stored in `localStorage` as `access_token`

---

## Pagination

Endpoints that support pagination return:
```json
{
  "total": <total_count>,
  "skip": <skip_value>,
  "limit": <limit_value>,
  "items": [...]
}
```

---

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Frontend File Reference

| File | Endpoints Used |
|------|----------------|
| `src/hooks/useAuth.tsx` | POST /api/v1/auth/token |
| `src/pages/ProductIdentities.tsx` | GET /api/v1/identities, POST /api/v1/identities |
| `src/pages/VariantManager.tsx` | GET /api/v1/variants, PATCH /api/v1/variants/{id}, POST /api/v1/variants |
| `src/pages/WarehouseOps.tsx` | POST /api/v1/inventory/receive, POST /api/v1/inventory/move, GET /api/v1/inventory/audit/{sku} |
| `src/pages/StockLookup.tsx` | GET /api/v1/inventory/audit/{sku} |

---

## Endpoints Configuration

API endpoints are centrally managed in `src/api/endpoints.ts`:

```typescript
export const AUTH = {
  LOGIN: '/token',
  ME: '/users/me',
}

export const INVENTORY = {
  AUDIT: (sku: string) => `/inventory/audit/${sku}`,
  RECEIVE: '/inventory/receive',
  MOVE: '/inventory/move',
  LOOKUP: '/inventory/lookup',
}

export const CATALOG = {
  IDENTITIES: '/identities',
  IDENTITY: (id: number) => `/identities/${id}`,
  VARIANTS: '/variants',
  VARIANT: (id: number) => `/variants/${id}`,
}
```

---

## Axios Client Configuration

The frontend uses a custom Axios client (`src/api/axiosClient.ts`) that:
- Automatically adds the Bearer token from localStorage
- Sends requests to `/api/v1` prefix
- Handles CORS for cross-origin requests from dev/prod environments

---

**Last Updated:** January 27, 2026  
**API Version:** v1
