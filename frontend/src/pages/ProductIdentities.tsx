import { useState } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import { DataGrid, GridColDef } from '@mui/x-data-grid'
import { Add } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axiosClient from '../api/axiosClient'
import { CATALOG } from '../api/endpoints'
import { ProductIdentity, ProductType } from '../types/inventory'
import { useAuth } from '../hooks/useAuth'

const columns: GridColDef[] = [
  { field: 'id', headerName: 'ID', width: 80 },
  {
    field: 'type',
    headerName: 'Type',
    width: 100,
    renderCell: (params) => {
      const labels: Record<string, string> = {
        P: 'Product',
        B: 'Bundle',
        K: 'Kit',
      }
      return labels[params.value] || params.value
    },
  },
  { field: 'lci', headerName: 'LCI', width: 150 },
  { field: 'upis_h', headerName: 'UPIS-H', flex: 1 },
  { field: 'hex_signature', headerName: 'Hex Signature', width: 150 },
  { field: 'created_at', headerName: 'Created', width: 180 },
]

interface ProductFamily {
  product_id: number
  base_name: string
}

export default function ProductIdentities() {
  const [dialogOpen, setDialogOpen] = useState(false)
  const [newIdentity, setNewIdentity] = useState({
    product_id: '' as string | number,
    type: 'P' as ProductType,
    lci: '',
  })
  const { hasRole } = useAuth()
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['identities'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.IDENTITIES)
      return response.data.items || []
    },
  })

  const { data: families } = useQuery({
    queryKey: ['families'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.FAMILIES)
      return response.data.items || []
    },
  })

  const createMutation = useMutation({
    mutationFn: async (data: { product_id: number; type: ProductType; lci?: number }) => {
      return axiosClient.post(CATALOG.IDENTITIES, data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['identities'] })
      setDialogOpen(false)
      setNewIdentity({ product_id: '', type: 'P', lci: '' })
    },
  })

  const handleCreate = () => {
    if (!newIdentity.product_id) return
    createMutation.mutate({
      product_id: Number(newIdentity.product_id),
      type: newIdentity.type,
      lci: newIdentity.type === 'P' && newIdentity.lci ? Number(newIdentity.lci) : undefined,
    })
  }

  const rows = (data || []).map((item: ProductIdentity) => ({
    id: item.id,
    ...item,
  }))

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Product Identities</Typography>
        {hasRole(['ADMIN']) && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setDialogOpen(true)}
          >
            Create Identity
          </Button>
        )}
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

      {/* Create Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)}>
        <DialogTitle>Create Product Identity</DialogTitle>
        <DialogContent sx={{ pt: 2, minWidth: 400 }}>
          <FormControl fullWidth sx={{ mb: 2, mt: 1 }}>
            <InputLabel>Product Family</InputLabel>
            <Select
              value={newIdentity.product_id}
              label="Product Family"
              onChange={(e) =>
                setNewIdentity({ ...newIdentity, product_id: e.target.value as number })
              }
            >
              {(families || []).map((family: ProductFamily) => (
                <MenuItem key={family.product_id} value={family.product_id}>
                  {family.product_id} - {family.base_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={newIdentity.type}
              label="Type"
              onChange={(e) =>
                setNewIdentity({ ...newIdentity, type: e.target.value as ProductType })
              }
            >
              <MenuItem value="P">Part</MenuItem>
              <MenuItem value="B">Bundle</MenuItem>
              <MenuItem value="K">Kit</MenuItem>
            </Select>
          </FormControl>
          {newIdentity.type === 'P' && (
            <TextField
              fullWidth
              label="LCI (Manufacturer Part Number)"
              value={newIdentity.lci}
              onChange={(e) =>
                setNewIdentity({ ...newIdentity, lci: e.target.value })
              }
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreate}
            disabled={createMutation.isPending || !newIdentity.product_id}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
