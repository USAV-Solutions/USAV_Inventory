import { useState, useMemo } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  Autocomplete,
  Alert,
  Typography,
  CircularProgress,
} from '@mui/material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axiosClient from '../../api/axiosClient'
import { CATALOG } from '../../api/endpoints'
import { Variant, ProductIdentity, ProductFamily } from '../../types/inventory'

interface CreateStockDialogProps {
  open: boolean
  onClose: () => void
  onSuccess?: (item: any) => void
}

interface EnhancedVariant extends Variant {
  identity?: ProductIdentity & { family?: ProductFamily }
  displayLabel?: string
}

type InventoryStatus = 'AVAILABLE' | 'SOLD' | 'RESERVED' | 'RMA' | 'DAMAGED'

interface StockFormData {
  variant_id: number | null
  serial_number: string
  location_code: string
  cost_basis: string
  status: InventoryStatus
  notes: string
}

const initialFormData: StockFormData = {
  variant_id: null,
  serial_number: '',
  location_code: '',
  cost_basis: '',
  status: 'AVAILABLE',
  notes: '',
}

const statusOptions: { value: InventoryStatus; label: string; color: string }[] = [
  { value: 'AVAILABLE', label: 'Available', color: '#4caf50' },
  { value: 'RESERVED', label: 'Reserved', color: '#ff9800' },
  { value: 'SOLD', label: 'Sold', color: '#f44336' },
  { value: 'RMA', label: 'RMA', color: '#9c27b0' },
  { value: 'DAMAGED', label: 'Damaged', color: '#757575' },
]

export default function CreateStockDialog({ open, onClose, onSuccess }: CreateStockDialogProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<StockFormData>(initialFormData)
  const [selectedVariant, setSelectedVariant] = useState<EnhancedVariant | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch variants
  const { data: variantsData, isLoading: variantsLoading } = useQuery({
    queryKey: ['variants'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.VARIANTS, {
        params: { limit: 1000 }
      })
      return response.data.items || []
    },
    enabled: open,
  })

  // Fetch identities
  const { data: identitiesData } = useQuery({
    queryKey: ['identities'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.IDENTITIES, {
        params: { limit: 1000 }
      })
      return response.data.items || []
    },
    enabled: open,
  })

  // Fetch families
  const { data: familiesData } = useQuery({
    queryKey: ['families'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.FAMILIES, {
        params: { limit: 1000 }
      })
      return response.data.items || []
    },
    enabled: open,
  })

  // Combine variant data with identity and family info
  const enhancedVariants: EnhancedVariant[] = useMemo(() => {
    if (!variantsData || !identitiesData || !familiesData) return []
    
    const identityMap = new Map<number, ProductIdentity & { family?: ProductFamily }>()
    const familyMap = new Map<number, ProductFamily>()
    
    familiesData.forEach((family: ProductFamily) => {
      familyMap.set(family.product_id, family)
    })
    
    identitiesData.forEach((identity: ProductIdentity) => {
      identityMap.set(identity.id, {
        ...identity,
        family: familyMap.get(identity.product_id),
      })
    })
    
    return variantsData.map((variant: Variant) => {
      const identity = identityMap.get(variant.identity_id)
      const productName = identity?.family?.base_name || 'Unknown'
      return {
        ...variant,
        identity,
        displayLabel: `${variant.full_sku} - ${productName}`,
      }
    })
  }, [variantsData, identitiesData, familiesData])

  // Create stock mutation
  const createStockMutation = useMutation({
    mutationFn: async (data: typeof formData) => {
      const payload = {
        variant_id: data.variant_id,
        serial_number: data.serial_number || null,
        location_code: data.location_code || null,
        cost_basis: data.cost_basis ? parseFloat(data.cost_basis) : null,
        status: data.status,
        notes: data.notes || null,
      }
      const response = await axiosClient.post('/inventory', payload)
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['inventory'] })
      handleClose()
      onSuccess?.(data)
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Failed to create stock item')
    },
  })

  const handleClose = () => {
    setFormData(initialFormData)
    setSelectedVariant(null)
    setError(null)
    onClose()
  }

  const handleSubmit = () => {
    if (!formData.variant_id) {
      setError('Please select a product variant')
      return
    }
    setError(null)
    createStockMutation.mutate(formData)
  }

  const handleVariantChange = (_: any, value: EnhancedVariant | null) => {
    setSelectedVariant(value)
    setFormData({
      ...formData,
      variant_id: value?.id || null,
    })
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>Create Stock Item</DialogTitle>
      <DialogContent>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, mt: 1 }}>
          {error && (
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Product Variant Selection */}
          <Autocomplete
            options={enhancedVariants}
            loading={variantsLoading}
            value={selectedVariant}
            onChange={handleVariantChange}
            getOptionLabel={(option) => option.displayLabel || option.full_sku || ''}
            isOptionEqualToValue={(option, value) => option.id === value.id}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Product Variant *"
                placeholder="Search by SKU or product name..."
                InputProps={{
                  ...params.InputProps,
                  endAdornment: (
                    <>
                      {variantsLoading ? <CircularProgress color="inherit" size={20} /> : null}
                      {params.InputProps.endAdornment}
                    </>
                  ),
                }}
              />
            )}
            renderOption={(props, option) => (
              <li {...props} key={option.id}>
                <Box>
                  <Typography variant="body2" fontFamily="monospace">
                    {option.full_sku}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {option.identity?.family?.base_name || 'Unknown Product'}
                  </Typography>
                </Box>
              </li>
            )}
          />

          {/* Serial Number */}
          <TextField
            label="Serial Number"
            value={formData.serial_number}
            onChange={(e) => setFormData({ ...formData, serial_number: e.target.value })}
            fullWidth
            placeholder="Enter serial number (optional)"
            helperText="Unique identifier for this specific unit"
          />

          {/* Location */}
          <TextField
            label="Location Code"
            value={formData.location_code}
            onChange={(e) => setFormData({ ...formData, location_code: e.target.value })}
            fullWidth
            placeholder="e.g., A1-B2, SHELF-03"
            helperText="Warehouse location for this item"
          />

          {/* Cost Basis */}
          <TextField
            label="Cost Basis"
            type="number"
            value={formData.cost_basis}
            onChange={(e) => setFormData({ ...formData, cost_basis: e.target.value })}
            fullWidth
            placeholder="0.00"
            helperText="Acquisition cost (optional)"
            inputProps={{ min: 0, step: 0.01 }}
          />

          {/* Status */}
          <FormControl fullWidth>
            <InputLabel>Status</InputLabel>
            <Select
              value={formData.status}
              label="Status"
              onChange={(e) => setFormData({ ...formData, status: e.target.value as InventoryStatus })}
            >
              {statusOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box
                      sx={{
                        width: 12,
                        height: 12,
                        borderRadius: '50%',
                        bgcolor: option.color,
                      }}
                    />
                    {option.label}
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          {/* Notes */}
          <TextField
            label="Notes"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            fullWidth
            multiline
            rows={2}
            placeholder="Additional notes about this item..."
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={createStockMutation.isPending || !formData.variant_id}
        >
          {createStockMutation.isPending ? 'Creating...' : 'Create Stock'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
