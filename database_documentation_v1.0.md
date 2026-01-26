# USAV Core Inventory Database Documentation

**Version:** 1.0
**Status:** Architecture Locked
**Architecture Type:** Hub & Spoke Middleware

## 1. System Overview

This database acts as the **central authority** for all USAV product data. It decouples **Internal Engineering Data** (what we build/repair) from **External Sales Data** (what we sell on Zoho/Amazon).

### The "Hub & Spoke" Philosophy

* **The Hub (This DB):** Owns the immutable "Product Identity" and physical inventory counts.
* **The Spokes (Zoho, Amazon, eBay):** Receive data updates from the Hub. They are *downstream* consumers.
* **Sync Direction:** `Internal DB`  `Zoho/External`. (We do not rely on Zoho as the master database).

---

## 2. Architecture & Schema Strategy

The schema implements the **Two-Layer Identification Model** defined in the [USAV SKU Specification (v2.5)](https://www.google.com/search?q=SKU.md).

### Layer 1: Product Identity (The "Engineering" Layer)

* **Table:** `PRODUCT_IDENTITY`
* **Purpose:** Defines **what an item IS**. This data is immutable once created.
* **Key Constraints:**
* **Uniqueness:** A combination of `product_id` + `type` + `lci` must be unique.
* **LCI Scope:** The Local Component Index (`lci`) is strictly scoped to a specific `product_id`.
* **HEX Signature:** Stores the deterministic 32-bit machine code derived *only* from identity fields.



### Layer 2: Product Variant (The "Sales" Layer)

* **Table:** `PRODUCT_VARIANT`
* **Purpose:** Defines **sellable configurations** (Color, Condition) of an Identity.
* **Relationship:** One Identity  Many Variants (e.g., A "Speaker" Identity can be "White/New", "Black/Used").
* **Full SKU:** Stores the computed string (e.g., `00845-P-1-WY-N`) used for warehouse picking and shipping labels.

---

## 3. Detailed Schema Reference

### A. Core Product Tables

#### `product_family`

*High-level grouping for products (e.g., "Bose Wave System").*
| Column | Type | Description |
| :--- | :--- | :--- |
| `product_id` | `INT` (PK) | The 5-digit ECWID ID (e.g., `00845`). Acts as the namespace root. |
| `base_name` | `VARCHAR` | Human-readable name (e.g., "Bose 201 Series"). |

#### `product_identity`

*Implementation of UPIS-H Layer 1.*
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `BIGINT` (PK) | Internal DB Key. |
| `product_id` | `INT` (FK) | Links to Family. |
| `type` | `ENUM` | `B` (Bundle), `P` (Part), `K` (Kit), `S` (Service), `Base` (Product). |
| `lci` | `INT` | Local Component Index (1-99). **NULL** unless Type=`P`. |
| `physical_class` | `CHAR(1)` | Registry Code: `E` (Electronics), `C` (Cover), etc.. |
| `generated_upis_h`| `VARCHAR` | The computed identity string (e.g., `00845-P-1`). **Unique Key**. |
| `hex_signature` | `CHAR(8)` | The 32-bit HEX encoding. Immutable.. |

#### `product_variant`

*Implementation of SKU Metadata Layer 2.*
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `BIGINT` (PK) | Internal DB Key. |
| `identity_id` | `BIGINT` (FK)| Links to the immutable Identity. |
| `color_code` | `VARCHAR(2)` | `BK`, `WY`, `SV` (See Color Index in Spec). |
| `condition_code` | `CHAR(1)` | `N` (New), `R` (Repair), or `NULL` (Used/Default). |
| `full_sku` | `VARCHAR` | The complete sellable string (e.g., `00845-P-1-WY-N`). **Unique Key**. |
| `zoho_item_id` | `VARCHAR` | Item ID on Zoho Inventory System|, 
| `zoho_sync_status` | `ENUM` | sync_status AS ENUM ('PENDING', 'SYNCED', 'ERROR', 'DIRTY')  |,
| `zoho_last_synced_at` | `TIMESTAMP` | |,
| `is_active` | `BOOLEAN` | Soft-delete flag (allows keeping history of discontinued variants). |

### B. Logic & Composition Tables

#### `bundle_component` (The Bill of Materials)

*Defines the "Recipe" for Bundles and Kits. Links to **Identity**, not Variant.*
| Column | Type | Description |
| :--- | :--- | :--- |
| `parent_identity_id` | `BIGINT` (FK) | The Bundle/Kit Identity (e.g., `02391-B`). |
| `child_identity_id` | `BIGINT` (FK) | The Component Identity (e.g., `00845`). |
| `quantity_required` | `INT` | How many of this component are needed. |
| `role` | `VARCHAR` | Context (e.g., "Primary", "Accessory", "Satellite"). |

### C. External Sync Tables (Goal 1)

#### `platform_listing`

*Manages the "Outbox" for syncing to Zoho, Amazon, etc.*
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `BIGINT` (PK) | |
| `variant_id` | `BIGINT` (FK) | The specific item being sold (e.g., White/New). |
| `platform` | `VARCHAR` | `ZOHO`, `AMAZON_US`, `EBAY_MOTOR`. |
| `external_ref_id` | `VARCHAR` | The ID on the remote platform (Zoho Item ID, ASIN). |
| `listing_price` | `DECIMAL` | The specific price for *this* platform. |
| `sync_status` | `ENUM` | `PENDING` (Needs push), `SYNCED` (Clean), `ERROR` (Retrying). |
| `platform_metadata` | `JSONB` | Platform-specific fields (e.g., Amazon Bullet Points, eBay Category ID). |

### D. Inventory Tables (Goal 2)

#### `inventory_item`

*Tracks specific physical instances.*
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `BIGINT` (PK) | |
| `serial_number` | `VARCHAR` | Manufacturer serial (if applicable). |
| `variant_id` | `BIGINT` (FK) | Links to what this item *is*. |
| `status` | `ENUM` | `AVAILABLE`, `SOLD`, `RESERVED` (in cart), `DAMAGED`. |
| `location_code` | `VARCHAR` | Warehouse location (e.g., "A1-S2"). |
| `cost_basis` | `DECIMAL` | Exact acquisition cost (for accounting/COGS). |

---

## 4. Key Workflows

### Workflow 1: Creating a New Part

1. **User Input:** Selects Product Family (`00845`), Type (`P`), and LCI (`1`).
2. **Validation:** DB checks `UNIQUE(product_id, type, lci)` constraint.
3. **Generation:**
* Compute `generated_upis_h` = `00845-P-1`.
* Compute `hex_signature` (Base-16 hash of identity fields).


4. **Storage:** Insert into `product_identity`.

### Workflow 2: Listing on Zoho

1. **Selection:** User selects a `product_variant` (e.g., `00845-P-1-WY-N`).
2. **Creation:** Insert row into `platform_listing` with:
* `platform` = 'ZOHO'
* `sync_status` = 'PENDING'


3. **Automation:** The background worker detects `sync_status='PENDING'`, pushes the payload to Zoho API.
4. **Confirmation:** On success, worker updates `sync_status` to 'SYNCED' and saves the returned Zoho Item ID into `external_ref_id`.

### Workflow 3: Handling Bundles

* **Scenario:** Order comes in for Bundle `02391-B`.
* **Logic:**
1. Look up `product_identity` for `02391-B`.
2. Query `bundle_component` to find the recipe (e.g., 1x `00845` Base Unit).
3. Check `inventory_item` for available instances of `00845` (Identity) matching the order's condition (Variant logic).
4. Mark those individual items as `SOLD`.



---

## 5. Developer Rules & Constraints

1. **Never Hardcode Logic:** Do not write code that assumes "Type P always has LCI". Check the `lci` column; if it is NULL, it is a base product.
2. **Hex Immutability:** The `hex_signature` must **never** change for a row. If the product identity changes, you must create a new row.
3. **Sync Latency:** Always assume the `platform_listing` data might be 5 minutes older than the external platform. Use the `sync_status` column to warn users if data is "dirty" (unsynced).
4. **JSONB Usage:** Use `platform_metadata` for anything that is specific to *only one* platform (e.g., `amazon_fulfillment_channel`). Do not add columns to the main table for single-platform features.