This updated documentation incorporates the new security layer, Role-Based Access Control (RBAC), and the transaction logging system we discussed.

# USAV Backend Architecture Documentation (v1.1)

## 1. Technology Stack Recommendations

* **Language:** Python 3.10+ (Recommended for strong data handling and Zoho SDK support).
* **Framework:** **FastAPI** (Recommended) or Flask. FastAPI provides automatic Swagger documentation and modern async support.
* **Authentication:** **OAuth2 with Password Flow + JWT Tokens** (Standard FastAPI security implementation).
* **ORM:** **SQLAlchemy** (Async) or **Tortoise ORM**.
* **Database Driver:** `asyncpg` (for high-performance PostgreSQL interaction).

---

## 2. Security & Authentication Architecture

### User Roles (RBAC)

The system implements a strict role-based hierarchy to protect the integrity of the immutable Identity Layer.

| Role | Permissions |
| --- | --- |
| `ADMIN` | **Full Access.** Can create `PRODUCT_FAMILY` and `PRODUCT_IDENTITY` (Layer 1). Can manage users. |
| `WAREHOUSE_OP` | **Operational Access.** Can `RECEIVE`, `MOVE`, and `AUDIT` physical inventory. **Read-only** access to Product Identities and Variants. |
| `SALES_REP` | **Commercial Access.** Can edit `PRODUCT_VARIANT` prices, descriptions, and metadata. **Read-only** access to stock levels. |
| `SYSTEM_BOT` | **Restricted Access.** Reserved for the **Zoho Sync Worker**. Can only update `zoho_sync_status`, `zoho_item_id`, and sync-related timestamps. |

### Auth Endpoints

#### `POST /token`

* **Purpose:** Authenticate a user and exchange credentials for a generic JWT access token.
* **Payload:** `username`, `password`
* **Response:** `{ "access_token": "eyJhbG...", "token_type": "bearer" }`

---

## 3. Component A: The Core REST API

### Module 1: Product Definition (Layer 1 - Identity)

Protecting the "Immutable" Layer is the primary security goal.

#### `POST /api/v1/families`

* **Auth:** `ADMIN` only.
* **Purpose:** Create a new product family namespace.
* **Payload:** `{ "product_id": 845, "base_name": "Bose 201 Series" }`

#### `POST /api/v1/identities`

* **Auth:** `ADMIN` only.
* **Purpose:** Create a Layer 1 Identity (UPIS-H).
* **Logic:**
1. Accepts `product_id`, `type`, `lci`.


2. DB Trigger automatically generates `hex_signature` and `generated_upis_h` to ensure determinism.


3. Returns the created Identity object.


* **Payload:** `{ "product_id": 845, "type": "P", "lci": 1, "physical_class": "E" }`

#### `GET /api/v1/identities/{upis_h}`

* **Auth:** Any authenticated user.
* **Purpose:** Lookup what an item *is* by its ID string (e.g., `00845-P-1`).

---

### Module 2: Variant Management (Layer 2 - Sales)

Manages sellable SKUs and the accounting link to Zoho.

#### `POST /api/v1/variants`

* **Auth:** `ADMIN` or `SALES_REP`.
* **Purpose:** Create a sellable configuration (Layer 2).
* **Logic:**
1. Validates `color_code` and `condition_code` against Enums.


2. Computes `full_sku` (e.g., `00845-P-1-WY-N`).


3. 
**Critical:** Sets `zoho_sync_status` to `'PENDING'` automatically upon creation.




* **Payload:**
```json
{
  "identity_id": 102,
  "color_code": "WY",
  "condition_code": "N",
  "listing_price": 150.00
}

```



#### `PATCH /api/v1/variants/{sku}`

* **Auth:** `ADMIN` or `SALES_REP`.
* **Purpose:** Update price or active status.
* **Logic:** If critical fields (Price, Description) change, the API must automatically set `zoho_sync_status = 'DIRTY'` to trigger the sync worker.

---

### Module 3: Physical Inventory (The "Warehouse" Layer)

*Manages stock on shelves and maintains the Transaction Log for auditability.*

#### `POST /api/v1/inventory/receive`

* **Auth:** `ADMIN` or `WAREHOUSE_OP`.
* **Purpose:** Intake new physical items.
* **Logic:**
1. Creates a new `INVENTORY_ITEM` record.
2. Creates a corresponding `INVENTORY_TRANSACTION` with type `'RECEIVE'`.
3. Links the transaction to `current_user.id` for accountability.


* **Payload:**
```json
{
  "variant_sku": "00845-P-1-WY-N",
  "serial_number": "SN-998877",
  "location_code": "A1-S2",
  "cost_basis": 45.00
}

```



#### `POST /api/v1/inventory/move`

* **Auth:** `ADMIN` or `WAREHOUSE_OP`.
* **Purpose:** Update location of an item.
* **Logic:**
1. Updates `INVENTORY_ITEM.location_id`.
2. Logs a `MOVE` transaction with `previous_location`, `new_location`, and `user_id`.


* **Payload:** `{ "serial_number": "...", "new_location": "B2-S1" }`

#### `GET /api/v1/inventory/audit/{sku}`

* **Auth:** Any authenticated user.
* **Purpose:** Returns total count + list of all serial numbers and locations for a specific SKU.

---

## 4. Component B: The Zoho Sync Worker (Daemon)

This standalone script runs continuously as the `SYSTEM_BOT` user.

### Authentication

The worker script must authenticate via the API (or connect directly to the DB) using the `SYSTEM_BOT` credentials. All DB updates made by this script are logged under this user ID, allowing you to distinguish between automated changes and human errors.

### Workflow 1: The "New Item" Pusher

* **Trigger:** `SELECT * FROM product_variant WHERE zoho_item_id IS NULL AND zoho_sync_status = 'PENDING'`
* **Action:**
1. Format payload for Zoho Inventory API (`POST /items`).
2. Map `full_sku` → Zoho `sku`.
3. Map `base_name` + Metadata → Zoho `name`.
4. Send Request.


* **On Success:**
1. Update DB: `zoho_item_id = [Response ID]`.
2. Update DB: `zoho_sync_status = 'SYNCED'`.



### Workflow 2: The "Update" Patcher

* **Trigger:** `SELECT * FROM product_variant WHERE zoho_sync_status = 'DIRTY'`
* **Action:**
1. Retrieve `zoho_item_id` from DB.
2. Format payload for Zoho API (`PUT /items/{id}`).
3. Send Request.


* **On Success:** Set `zoho_sync_status = 'SYNCED'`.

---

## 5. Development Roadmap (Updated)

### Sprint 1: "Foundation & Security"

1. **Script:** `init_db.py` - Sets up Postgres schema, Triggers, and **seed Users** (`admin`, `zoho_worker`).
2. **API:** Implement `POST /token` (Login) and Auth Middleware (Dependency Injection).
3. **API:** Implement `POST /families`, `POST /identities` (Protected by `ADMIN` role).

### Sprint 2: "Sales & Sync"

1. **API:** Implement `POST /variants` (Auto-sets Pending status).
2. **Worker:** Implement `zoho_worker.py` with `SYSTEM_BOT` authentication.
3. **Test:** Create a Variant via API -> Verify `PENDING` status -> Run Worker -> Verify `SYNCED` status and `zoho_item_id` population.

### Sprint 3: "Warehouse Operations"

1. **API:** Implement `POST /inventory/receive` and `/move`.
2. **Logic:** Ensure every inventory action inserts a row into `INVENTORY_TRANSACTION` with the correct `user_id`.
3. **Test:** Login as `WAREHOUSE_OP` -> Move an item -> Login as `ADMIN` -> Verify Audit Log shows the move and the user.

---

## 6. Directory Structure Proposal

```text
/backend-usav
├── /app
│   ├── /api
│   │   ├── /v1
│   │   │   ├── auth.py         # Login & Token endpoints
│   │   │   ├── products.py     # Families, Identities, Variants
│   │   │   └── inventory.py    # Receive, Move, Audit
│   │   └── deps.py             # Auth dependencies (get_current_user, require_admin)
│   ├── /core
│   │   ├── security.py         # JWT generation & Password hashing
│   │   ├── config.py           # DB & Zoho Credentials
│   │   └── models.py           # SQLAlchemy Models
│   └── main.py                 # FastAPI Entry point
├── /workers
│   ├── zoho_sync.py            # The Background Daemon
│   └── zoho_client.py          # Zoho API Wrapper
├── /database
│   ├── schema.sql              # DDL (including Users & Transactions)
│   └── init_data.py            # Script to seed initial users
├── requirements.txt
└── .env

```