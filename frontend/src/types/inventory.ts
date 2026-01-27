export type ZohoSyncStatus = 'SYNCED' | 'PENDING' | 'ERROR' | 'DIRTY'
export type ProductType = 'P' | 'B' | 'K'
export type ItemCondition = 'NEW' | 'REFURBISHED' | 'USED'
export type ItemStatus = 'IN_STOCK' | 'SOLD' | 'RESERVED' | 'DAMAGED'

export interface ProductIdentity {
  id: number
  type: ProductType
  lci?: string
  upis_h: string
  hex_signature: string
  created_at: string
}

export interface Variant {
  id: number
  identity_id: number
  full_sku: string
  condition: ItemCondition
  price: number
  zoho_status: ZohoSyncStatus
  zoho_error?: string
  created_at: string
  updated_at: string
}

export interface InventoryItem {
  id: number
  serial_number: string
  variant_id: number
  location_code: string
  status: ItemStatus
  received_at: string
  updated_at: string
}

export interface InventoryAudit {
  sku: string
  items: InventoryItem[]
  total_count: number
}
