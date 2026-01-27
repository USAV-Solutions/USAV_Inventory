# USAV Inventory Frontend

React + TypeScript + Material UI frontend for the USAV Inventory System.

## Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will run on http://localhost:3000 and proxy API requests to http://localhost:8000.

### Build

```bash
npm run build
```

## Features

- **Authentication**: JWT-based login with role-based access control
- **Dashboard**: Quick actions based on user role
- **Warehouse Operations**: Receive, Move, and Audit inventory items with barcode scanner support
- **Stock Lookup**: Search inventory by SKU
- **Product Identities**: Manage product families (Admin/Sales)
- **Variant Manager**: Manage variants with Zoho sync status visualization

## User Roles

- `ADMIN` - Full access to all features
- `WAREHOUSE_OP` - Access to warehouse operations and stock lookup
- `SALES_REP` - Access to catalog management (identities and variants)
