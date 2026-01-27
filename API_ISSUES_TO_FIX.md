# API Endpoints - Issues & Mismatches

## Summary
This document identifies endpoints that are documented or expected but are **not properly implemented** or **don't work as expected**.

**Date:** January 27, 2026  
**Status:** ✅ ALL PHASES COMPLETE

---

## CRITICAL ISSUES (Frontend Cannot Function)

### ✅ Issue #1: Missing Warehouse Operations Endpoints - FIXED

**Impact:** ~~HIGH - Warehouse Operations page is completely non-functional~~ RESOLVED  
**Fixed:** January 27, 2026

#### Implemented Endpoints:

1. **`POST /api/v1/inventory/receive`** ✅ IMPLEMENTED
   - **Added To:** `Backend/app/api/routes/inventory.py`
   - **Schemas:** `InventoryReceiveRequest`, `InventoryReceiveResponse`
   - **Purpose:** Intake new physical items into inventory
   - **Request:**
     ```json
     {
       "serial_number": "SN12345678",
       "variant_sku": "00845-P-1-WY-N",
       "location_code": "A1-001",
       "cost_basis": 99.99
     }
     ```
   - **Response:**
     ```json
     {
       "id": 123,
       "serial_number": "SN12345678",
       "sku": "00845-P-1-WY-N",
       "location_code": "A1-001",
       "status": "AVAILABLE",
       "received_at": "2026-01-27T14:00:00Z"
     }
     ```
   - **Error Handling:**
     - 409 Conflict - Serial number already exists
     - 404 Not Found - Variant SKU not found

2. **`POST /api/v1/inventory/move`** ✅ IMPLEMENTED
   - **Added To:** `Backend/app/api/routes/inventory.py`
   - **Schemas:** `InventoryMoveRequest`, `InventoryMoveResponse`
   - **Purpose:** Update location of a physical item
   - **Request:**
     ```json
     {
       "serial_number": "SN12345678",
       "new_location": "B2-005"
     }
     ```
   - **Response:**
     ```json
     {
       "serial_number": "SN12345678",
       "previous_location": "A1-001",
       "new_location": "B2-005",
       "moved_at": "2026-01-27T14:05:00Z"
     }
     ```
   - **Error Handling:**
     - 404 Not Found - Serial number not found

3. **`GET /api/v1/inventory/audit/{sku_or_serial}`** ✅ IMPLEMENTED
   - **Added To:** `Backend/app/api/routes/inventory.py`
   - **Schemas:** `InventoryAuditItem`, `InventoryAuditResponse`
   - **Purpose:** Lookup inventory by SKU or serial number
   - **Request:** `GET /api/v1/inventory/audit/00845-P-1-WY-N`
   - **Response:**
     ```json
     {
       "items": [
         {
           "id": 123,
           "serial_number": "SN12345678",
           "location_code": "A1-001",
           "status": "AVAILABLE",
           "received_at": "2026-01-20T10:30:00Z",
           "variant_id": 45,
           "full_sku": "00845-P-1-WY-N"
         }
       ],
       "total_count": 1
     }
     ```
   - **Behavior:** First tries serial number lookup (exact), then SKU lookup (all items for variant)

---

### ✅ Issue #2: Variants Endpoint Response Format - FIXED

**Impact:** ~~MEDIUM - Variant Manager page shows no data~~ RESOLVED
**Fixed:** January 27, 2026

#### Solution Applied:

**Endpoint:** `GET /api/v1/variants`

- **Frontend Code Updated To:**
  ```tsx
  const { data, isLoading } = useQuery({
    queryKey: ['variants'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.VARIANTS)
      return response.data.items || []  // Extracts items from PaginatedResponse
    },
  })
  ```
  
- **File Changed:** `frontend/src/pages/VariantManager.tsx` (line 90)
- **Pattern:** All list endpoints return `PaginatedResponse`, frontend extracts `items` array

---

## MEDIUM PRIORITY ISSUES

### ✅ Issue #3: Response Format Standardization - DOCUMENTED

**Impact:** ~~MEDIUM - Frontend/Backend response format mismatch~~ RESOLVED
**Status:** All endpoints documented and frontend adapted

#### Standardized Pattern:

**All list endpoints return `PaginatedResponse`:**
```json
{
  "total": 10,
  "skip": 0,
  "limit": 100,
  "items": [...]  
}
```

**Frontend extraction pattern:**
```tsx
const response = await axiosClient.get(endpoint)
return response.data.items || []
```

| Endpoint | Returns | Frontend Status |
|----------|---------|------------------|
| `GET /api/v1/identities` | `PaginatedResponse` | ✅ Extracts `items` |
| `GET /api/v1/variants` | `PaginatedResponse` | ✅ Extracts `items` |
| `GET /api/v1/inventory` | `PaginatedResponse` | ✅ (not used yet) |
| `GET /api/v1/inventory/audit/{sku}` | `{ items, total_count }` | ✅ Custom format |
| `GET /api/v1/inventory/serial/{serial}` | `InventoryItemResponse` | ✅ Single item |

---

## LOW PRIORITY ISSUES

### ✅ Issue #4: All Endpoints Now Documented

**Impact:** ~~LOW - These exist but aren't documented for frontend use~~ RESOLVED
**Status:** All endpoints documented in `Inventory_API_Documentation.md`

| Endpoint | Purpose | Documented |
|----------|---------|---|
| `GET /api/v1/inventory/{item_id}` | Get single item | ✅ |
| `GET /api/v1/inventory/serial/{serial_number}` | Get by serial | ✅ |
| `PATCH /api/v1/inventory/{item_id}` | Generic update | ✅ |
| `DELETE /api/v1/inventory/{item_id}` | Delete item | ✅ |
| `POST /api/v1/inventory/{item_id}/reserve` | Reserve item | ✅ |
| `POST /api/v1/inventory/{item_id}/sell` | Mark sold | ✅ |
| `GET /api/v1/inventory/summary/{variant_id}` | Summary | ✅ |
| `GET /api/v1/inventory/value/total` | Inventory value | ✅ |

---

## Implementation Roadmap

### Phase 1: CRITICAL (Required for MVP) ✅ COMPLETE

**Priority:** ~~URGENT - Frontend is broken without these~~ DONE  
**Completed:** January 27, 2026

- [x] **Create `POST /api/v1/inventory/receive`**
  - Accepts `serial_number`, `variant_sku`, `location_code`, `cost_basis`
  - Creates `InventoryItem` record with AVAILABLE status
  - Returns item details including ID and received timestamp
  
- [x] **Create `POST /api/v1/inventory/move`**
  - Accepts `serial_number` and `new_location`
  - Updates location, returns previous and new location
  - Returns move confirmation with timestamp
  
- [x] **Create `GET /api/v1/inventory/audit/{sku_or_serial}`**
  - Search by SKU or serial number
  - Returns array of matching items in format: `{ items: [...], total_count }`
  - Supports both serial number (exact) and SKU lookup (all items for variant)

### Phase 2: CONSISTENCY (Should fix for stability) ✅ COMPLETE

**Priority:** ~~HIGH - Backend code clarity~~ DONE
**Completed:** January 27, 2026

- [x] **Standardize response formats across all list endpoints**
  - All list endpoints return `PaginatedResponse` with `items` array
  - Frontend updated to extract `items` from all list responses
  - Custom `audit` endpoint returns `{ items: [...], total_count }` format
  
- [x] **Document actual endpoint responses**
  - Updated `Inventory_API_Documentation.md` with actual response formats
  - Added examples of successful responses for all endpoints

### Phase 3: CLEANUP (Nice to have) ✅ COMPLETE

**Priority:** ~~LOW - Code quality~~ DONE
**Completed:** January 27, 2026

- [x] **Document all unused/specialized endpoints**
  - All endpoints documented in `Inventory_API_Documentation.md`
  - Each endpoint includes auth requirements, purpose, and response format

---

## Files to Update

### Backend Implementation
- `Backend/app/api/routes/inventory.py` - Add receive, move, audit endpoints

### Documentation
- `Backend/Inventory_API_Documentation.md` - Update with actual implementation
- `FRONTEND_API_ENDPOINTS.md` - Already accurate after receive/move/audit are implemented

### Frontend (Already Fixed)
- `frontend/src/pages/ProductIdentities.tsx` - Extract `items` from paginated response ✓
- `frontend/src/pages/VariantManager.tsx` - Extract `items` from paginated response ✓

---

## Testing Checklist

After implementation, verify:

- [ ] Warehouse Operations page - Receive mode works
- [ ] Warehouse Operations page - Move mode works  
- [ ] Warehouse Operations page - Audit mode works
- [ ] Stock Lookup page - Search by SKU returns results
- [ ] Stock Lookup page - Search by serial returns results
- [ ] Variant Manager - Lists all variants properly
- [ ] Product Identities - Lists all identities properly
- [ ] All responses match expected format in FRONTEND_API_ENDPOINTS.md

---

**Last Updated:** January 27, 2026  
**Status:** ✅ Phase 1 Complete → ✅ Phase 2 Complete → ✅ Phase 3 Complete
