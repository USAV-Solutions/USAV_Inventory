// Auth endpoints
export const AUTH = {
  LOGIN: '/token',
  ME: '/users/me',
}

// Inventory endpoints
export const INVENTORY = {
  AUDIT: (sku: string) => `/inventory/audit/${sku}`,
  RECEIVE: '/inventory/receive',
  MOVE: '/inventory/move',
  LOOKUP: '/inventory/lookup',
}

// Catalog endpoints
export const CATALOG = {
  FAMILIES: '/families',
  FAMILY: (id: number) => `/families/${id}`,
  IDENTITIES: '/identities',
  IDENTITY: (id: number) => `/identities/${id}`,
  VARIANTS: '/variants',
  VARIANT: (id: number) => `/variants/${id}`,
}
