This documentation outlines the frontend architecture for the **USAV Inventory System**. In alignment with our Agile strategy, this document focuses on the requirements for **Phase 1 (Inventory & Zoho Sync)**, prioritizing functional internal tools over public-facing aesthetics.

# USAV Frontend Architecture Documentation (v1.0)

## 1. Technology Stack Recommendations

For a data-heavy internal dashboard running on an HP Server/Proxmox environment, stability and "dense" data display are key.

* **Framework:** **React** + **TypeScript**.
* *Why:* TypeScript is non-negotiable for ensuring the frontend "knows" your complex data shapes (UPIS-H, Variants) and prevents bugs.


* **UI Component Library:** **Material UI (MUI)**.
* *Why:* It provides enterprise-grade **Data Grids** (essential for inventory lists) and pre-built form components out of the box. We don't want to waste time styling CSS for a warehouse tool.


* **State Management/Data Fetching:** **TanStack Query (React Query)**.
* *Why:* Inventory data is "Server State." You need features like auto-refetching (polling stock levels) and caching without writing complex `useEffect` chains.


* **HTTP Client:** **Axios**.
* *Why:* Easy setup for "Interceptors" to automatically attach your JWT Auth Tokens to every request.



---

## 2. Application Architecture

### Directory Structure

```text
/frontend-usav
├── /src
│   ├── /api
│   │   ├── axiosClient.ts   # Interceptors for JWT
│   │   └── endpoints.ts     # Definition of all Backend URLs
│   ├── /components
│   │   ├── /common          # Buttons, Inputs, Layouts
│   │   └── /guards          # ProtectedRoute (RBAC logic)
│   ├── /features
│   │   ├── /auth            # Login Screen
│   │   ├── /inventory       # Receive/Move forms
│   │   └── /catalog         # Product Identity & Variant tables
│   ├── /hooks               # Custom hooks (useAuth, useScan)
│   ├── /pages               # The actual routed views
│   └── App.tsx

```

---

## 3. Core Features & Page Requirements (Phase 1)

The frontend is divided into three "Portals" based on the user roles defined in the backend.

### A. The "Gatekeeper" (Authentication)

* **Route:** `/login`
* **Function:**
* Simple form: Username/Password.
* On Submit: POST to `/token`.
* On Success: Store JWT in `localStorage`, decode the JWT to get the user's **Role** (e.g., `WAREHOUSE_OP`), and redirect to the appropriate dashboard.



### B. The Warehouse Portal (Role: `WAREHOUSE_OP`)

*Focus: Speed, large buttons, "Scan-ready" inputs.*

#### 1. Inventory Dashboard / Scan Tool

* **Route:** `/warehouse/ops`
* **UI Layout:**
* **Mode Toggle:** Switch between "Receive Mode", "Move Mode", and "Audit Mode".
* **The "Global Input":** A large, auto-focused text field designed for barcode scanners.


* **Workflow (Move Mode):**
1. User scans Item Barcode  App queries `/api/v1/inventory/audit/{sku}`.
2. App displays item details (Green Card).
3. User scans Location Barcode  App sends POST `/api/v1/inventory/move`.
4. Success Sound/Flash.



#### 2. Stock Lookup

* **Route:** `/warehouse/lookup`
* **UI Layout:** A Search Bar + Data Grid showing `Serial Number`, `Location`, `Status` for a searched SKU.

---

### C. The Catalog Portal (Role: `SALES_REP` & `ADMIN`)

*Focus: Data integrity, Zoho Sync visibility.*

#### 1. Product Family & Identity Manager

* **Route:** `/catalog/identities`
* **UI Layout:**
* **Data Grid:** Columns for `Product ID`, `Type`, `LCI`, `Generated UPIS-H`, `Hex Signature`.
* **Create Button (Admin Only):** Opens a Modal to define a new Identity.
* *Validation:* Ensure `LCI` is only requested if `Type = P`.





#### 2. Variant & Sync Manager

* **Route:** `/catalog/variants`
* **UI Layout:**
* **Data Grid:** This is the most important view for sales.
* **Columns:** `Full SKU`, `Price`, `Condition`, `Zoho Status`.
* **Zoho Status Column:** Visual "Chips":
* 🟢 **SYNCED:** (Green) - All good.
* 🟡 **PENDING:** (Yellow) - Waiting for Worker.
* 🔴 **ERROR:** (Red) - Hover to see error message.




* **Action:** "Edit Price" button. modifying this must visually change the status to "DIRTY" (Yellow) immediately using Optimistic UI updates.



---

## 4. Critical UX/Dev Requirements

### 1. The "Scanner Hook"

Physical barcode scanners usually act like keyboards (they type the string and hit Enter). You need a global listener or a specialized React Hook to handle this.

* *Requirement:* Ensure the "Action Input" field on the Warehouse page always claims focus so the user doesn't have to click it before scanning.

### 2. Role-Based Access Control (RBAC) UI

You must build a `<ProtectedRoute>` wrapper component.

```tsx
// Pseudocode Example
<Routes>
  {/* Public */}
  <Route path="/login" element={<Login />} />

  {/* Warehouse Only */}
  <Route element={<RoleGuard allowedRoles={['WAREHOUSE_OP', 'ADMIN']} />}>
     <Route path="/warehouse/ops" element={<WarehouseOps />} />
  </Route>

  {/* Sales/Admin Only */}
  <Route element={<RoleGuard allowedRoles={['SALES_REP', 'ADMIN']} />}>
     <Route path="/catalog/variants" element={<VariantManager />} />
  </Route>
</Routes>

```

### 3. Error Handling (The "Red Box")

If the Backend API rejects a move (e.g., "Location does not exist" or "Item already sold"), the frontend must display a **Blocking Alert Modal**. Warehouse environments can be loud; a subtle toast notification might be missed.

---

## 5. Development Roadmap (Agile Frontend)

### Sprint 1: "Hello World"

1. Initialize React + Vite + MUI.
2. Set up `axios` instance with JWT interceptor.
3. Build Login Page & Routing.
4. **Deliverable:** A user can log in and see a blank dashboard specific to their role.

### Sprint 2: "The Catalog"

1. Build `IdentityTable` and `VariantTable` components using MUI DataGrid.
2. Connect `VariantTable` to `GET /api/v1/variants`.
3. Add "Create Variant" Modal.
4. **Deliverable:** Sales team can see what products exist and their Zoho Sync status.

### Sprint 3: "The Scanner"

1. Build the `WarehouseOps` page.
2. Implement the "Receive Item" form (Input Serial -> POST /receive).
3. Implement the "Move Item" form (Scan Serial -> Scan Location -> POST /move).
4. **Deliverable:** Warehouse team can digitally track inventory movement.