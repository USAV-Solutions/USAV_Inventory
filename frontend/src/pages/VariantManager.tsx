import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tooltip,
} from '@mui/material'
import { DataGrid, GridColDef, GridRenderCellParams } from '@mui/x-data-grid'
import { Add, Edit } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axiosClient from '../api/axiosClient'
import { CATALOG } from '../api/endpoints'
import { Variant, ZohoSyncStatus } from '../types/inventory'

const getSyncStatusChip = (status: ZohoSyncStatus, error?: string) => {
  type ChipColor = 'success' | 'warning' | 'error' | 'default'
  const configs: Record<ZohoSyncStatus, { color: ChipColor; label: string }> = {
    SYNCED: { color: 'success', label: '🟢 SYNCED' },
    PENDING: { color: 'warning', label: '🟡 PENDING' },
    ERROR: { color: 'error', label: '🔴 ERROR' },
    DIRTY: { color: 'warning', label: '🟡 DIRTY' },
  }
  const config = configs[status] || { color: 'default' as ChipColor, label: status }
  
  const chip = <Chip size="small" color={config.color} label={config.label} />
  
  if (status === 'ERROR' && error) {
    return <Tooltip title={error}>{chip}</Tooltip>
  }
  return chip
}

export default function VariantManager() {
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [selectedVariant, setSelectedVariant] = useState<Variant | null>(null)
  const [editPrice, setEditPrice] = useState('')
  const [newVariant, setNewVariant] = useState({
    identity_id: '',
    condition: 'NEW',
    price: '',
  })
  const queryClient = useQueryClient()

  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID', width: 80 },
    { field: 'full_sku', headerName: 'Full SKU', flex: 1 },
    { field: 'condition', headerName: 'Condition', width: 120 },
    {
      field: 'price',
      headerName: 'Price',
      width: 100,
      renderCell: (params: GridRenderCellParams) => `$${params.value?.toFixed(2) || '0.00'}`,
    },
    {
      field: 'zoho_status',
      headerName: 'Zoho Status',
      width: 140,
      renderCell: (params: GridRenderCellParams<Variant>) =>
        getSyncStatusChip(params.value as ZohoSyncStatus, params.row.zoho_error),
    },
    { field: 'updated_at', headerName: 'Updated', width: 180 },
    {
      field: 'actions',
      headerName: 'Actions',
      width: 100,
      renderCell: (params: GridRenderCellParams<Variant>) => (
        <Button
          size="small"
          startIcon={<Edit />}
          onClick={() => handleEditClick(params.row)}
        >
          Edit
        </Button>
      ),
    },
  ]

  const { data, isLoading } = useQuery({
    queryKey: ['variants'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.VARIANTS)
      return response.data.items || []
    },
  })

  const updateMutation = useMutation({
    mutationFn: async ({ id, price }: { id: number; price: number }) => {
      return axiosClient.patch(CATALOG.VARIANT(id), { price })
    },
    onMutate: async ({ id, price }) => {
      // Optimistic update
      await queryClient.cancelQueries({ queryKey: ['variants'] })
      const previous = queryClient.getQueryData(['variants'])
      
      queryClient.setQueryData(['variants'], (old: Variant[] | undefined) =>
        old?.map((v) =>
          v.id === id ? { ...v, price, zoho_status: 'DIRTY' as ZohoSyncStatus } : v
        )
      )
      
      return { previous }
    },
    onError: (_, __, context) => {
      queryClient.setQueryData(['variants'], context?.previous)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['variants'] })
      setEditDialogOpen(false)
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: { identity_id: number; condition: string; price: number }) => {
      return axiosClient.post(CATALOG.VARIANTS, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variants'] })
      setCreateDialogOpen(false)
      setNewVariant({ identity_id: '', condition: 'NEW', price: '' })
    },
  })

  const handleEditClick = (variant: Variant) => {
    setSelectedVariant(variant)
    setEditPrice(variant.price.toString())
    setEditDialogOpen(true)
  }

  const handleSavePrice = () => {
    if (selectedVariant) {
      updateMutation.mutate({
        id: selectedVariant.id,
        price: parseFloat(editPrice),
      })
    }
  }

  const handleCreate = () => {
    createMutation.mutate({
      identity_id: parseInt(newVariant.identity_id),
      condition: newVariant.condition,
      price: parseFloat(newVariant.price),
    })
  }

  const rows = (data || []).map((item: Variant) => ({
    id: item.id,
    ...item,
  }))

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Variant Manager</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Variant
        </Button>
      </Box>

      <Paper sx={{ height: 600 }}>
        <DataGrid
          rows={rows}
          columns={columns}
          loading={isLoading}
          pageSizeOptions={[10, 25, 50]}
          initialState={{
            pagination: { paginationModel: { pageSize: 25 } },
          }}
          disableRowSelectionOnClick
        />
      </Paper>

      {/* Edit Price Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>Edit Price</DialogTitle>
        <DialogContent sx={{ pt: 2, minWidth: 300 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            SKU: {selectedVariant?.full_sku}
          </Typography>
          <TextField
            fullWidth
            label="Price"
            type="number"
            value={editPrice}
            onChange={(e) => setEditPrice(e.target.value)}
            InputProps={{ startAdornment: '$' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleSavePrice}
            disabled={updateMutation.isPending}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Create Variant Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)}>
        <DialogTitle>Create Variant</DialogTitle>
        <DialogContent sx={{ pt: 2, minWidth: 400 }}>
          <TextField
            fullWidth
            label="Identity ID"
            type="number"
            value={newVariant.identity_id}
            onChange={(e) =>
              setNewVariant({ ...newVariant, identity_id: e.target.value })
            }
            sx={{ mb: 2, mt: 1 }}
          />
          <TextField
            fullWidth
            select
            label="Condition"
            value={newVariant.condition}
            onChange={(e) =>
              setNewVariant({ ...newVariant, condition: e.target.value })
            }
            sx={{ mb: 2 }}
            SelectProps={{ native: true }}
          >
            <option value="NEW">New</option>
            <option value="REFURBISHED">Refurbished</option>
            <option value="USED">Used</option>
          </TextField>
          <TextField
            fullWidth
            label="Price"
            type="number"
            value={newVariant.price}
            onChange={(e) =>
              setNewVariant({ ...newVariant, price: e.target.value })
            }
            InputProps={{ startAdornment: '$' }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreate}
            disabled={createMutation.isPending}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
