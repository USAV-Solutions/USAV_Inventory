import { useState, useMemo } from 'react'
import {
  Box,
  Typography,
  Button,
  Paper,
  TextField,
  InputAdornment,
  ToggleButton,
  ToggleButtonGroup,
  Chip,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
} from '@mui/material'
import {
  Add,
  Search,
  ViewList,
  ViewModule,
  ExpandMore,
  ExpandLess,
} from '@mui/icons-material'
import { useQuery } from '@tanstack/react-query'
import axiosClient from '../api/axiosClient'
import { CATALOG } from '../api/endpoints'
import { Variant, ProductIdentity, ProductFamily, ProductType } from '../types/inventory'
import { useAuth } from '../hooks/useAuth'
import CreateProductDialog from '../components/inventory/CreateProductDialog'

type ViewMode = 'list' | 'grouped'

interface ExpandedRowProps {
  parentUpisH: string
  variants: EnhancedVariant[]
}

interface EnhancedVariant extends Variant {
  identity?: ProductIdentity & { family?: ProductFamily }
}

interface GroupedItem {
  parent_upis_h: string
  name: string
  type: ProductType
  brand?: string
  alias_count: number
  variants: EnhancedVariant[]
}

const getTypeLabel = (type: ProductType): string => {
  const labels: Record<ProductType, string> = {
    Product: 'Product',
    P: 'Part',
    B: 'Bundle',
    K: 'Kit',
  }
  return labels[type] || type
}

const getTypeColor = (type: ProductType): 'primary' | 'secondary' | 'success' | 'warning' => {
  const colors: Record<ProductType, 'primary' | 'secondary' | 'success' | 'warning'> = {
    Product: 'primary',
    P: 'secondary',
    B: 'success',
    K: 'warning',
  }
  return colors[type] || 'primary'
}

const getSyncStatusChip = (status: string) => {
  type ChipColor = 'success' | 'warning' | 'error' | 'default'
  const configs: Record<string, { color: ChipColor; label: string }> = {
    SYNCED: { color: 'success', label: '🟢 Synced' },
    PENDING: { color: 'warning', label: '🟡 Pending' },
    ERROR: { color: 'error', label: '🔴 Error' },
    DIRTY: { color: 'warning', label: '🟡 Dirty' },
  }
  const config = configs[status] || { color: 'default' as ChipColor, label: status }
  return <Chip size="small" color={config.color} label={config.label} />
}

function ExpandedRow({ parentUpisH, variants }: ExpandedRowProps) {
  return (
    <TableRow>
      <TableCell colSpan={7} sx={{ py: 0, bgcolor: 'grey.50' }}>
        <Box sx={{ py: 2, px: 4 }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Variants for {parentUpisH}
          </Typography>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Full SKU</TableCell>
                <TableCell>Color</TableCell>
                <TableCell>Condition</TableCell>
                <TableCell>Zoho Status</TableCell>
                <TableCell>Active</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {variants.map((variant) => (
                <TableRow key={variant.id}>
                  <TableCell>{variant.full_sku}</TableCell>
                  <TableCell>{variant.color_code || '-'}</TableCell>
                  <TableCell>{variant.condition_code || 'Used'}</TableCell>
                  <TableCell>{getSyncStatusChip(variant.zoho_sync_status)}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={variant.is_active ? 'Active' : 'Inactive'}
                      color={variant.is_active ? 'success' : 'default'}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Box>
      </TableCell>
    </TableRow>
  )
}

export default function InventoryManagement() {
  const [viewMode, setViewMode] = useState<ViewMode>('list')
  const [searchQuery, setSearchQuery] = useState('')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(25)
  const { hasRole } = useAuth()

  // Fetch variants with identity data
  const { data: variantsData, isLoading: variantsLoading } = useQuery({
    queryKey: ['variants'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.VARIANTS, {
        params: { limit: 1000 }
      })
      return response.data.items || []
    },
  })

  // Fetch identities with family data
  const { data: identitiesData, isLoading: identitiesLoading } = useQuery({
    queryKey: ['identities'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.IDENTITIES, {
        params: { limit: 1000 }
      })
      return response.data.items || []
    },
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
  })

  // Combine data
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
    
    return variantsData.map((variant: Variant) => ({
      ...variant,
      identity: identityMap.get(variant.identity_id),
    }))
  }, [variantsData, identitiesData, familiesData])

  // Filter by search query
  const filteredVariants = useMemo(() => {
    if (!searchQuery.trim()) return enhancedVariants
    
    const query = searchQuery.toLowerCase()
    return enhancedVariants.filter((variant) => {
      const name = variant.identity?.family?.base_name?.toLowerCase() || ''
      const sku = variant.full_sku?.toLowerCase() || ''
      const upisH = variant.identity?.generated_upis_h?.toLowerCase() || ''
      const brand = variant.identity?.family?.brand?.name?.toLowerCase() || ''
      
      return name.includes(query) || 
             sku.includes(query) || 
             upisH.includes(query) ||
             brand.includes(query)
    })
  }, [enhancedVariants, searchQuery])

  // Group variants by parent UPIS-H
  const groupedData: GroupedItem[] = useMemo(() => {
    const groups = new Map<string, GroupedItem>()
    
    filteredVariants.forEach((variant) => {
      const upisH = variant.identity?.generated_upis_h || 'Unknown'
      
      if (!groups.has(upisH)) {
        groups.set(upisH, {
          parent_upis_h: upisH,
          name: variant.identity?.family?.base_name || 'Unknown',
          type: variant.identity?.type || 'Product',
          brand: variant.identity?.family?.brand?.name,
          alias_count: 0,
          variants: [],
        })
      }
      
      const group = groups.get(upisH)!
      group.variants.push(variant)
      group.alias_count = group.variants.length
    })
    
    return Array.from(groups.values())
  }, [filteredVariants])

  const handleToggleExpand = (upisH: string) => {
    setExpandedRows((prev) => {
      const next = new Set(prev)
      if (next.has(upisH)) {
        next.delete(upisH)
      } else {
        next.add(upisH)
      }
      return next
    })
  }

  const handleChangePage = (_: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const isLoading = variantsLoading || identitiesLoading

  // Paginated data
  const paginatedListData = filteredVariants.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )
  const paginatedGroupedData = groupedData.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  )

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Inventory Management</Typography>
        {hasRole(['ADMIN']) && (
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Add New Item
          </Button>
        )}
      </Box>

      {/* Search and View Toggle */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField
            placeholder="Search by name, SKU, or brand..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            sx={{ flexGrow: 1, minWidth: 300 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, value) => value && setViewMode(value)}
            size="small"
          >
            <ToggleButton value="list">
              <Tooltip title="List View">
                <ViewList />
              </Tooltip>
            </ToggleButton>
            <ToggleButton value="grouped">
              <Tooltip title="Group by Parent Product">
                <ViewModule />
              </Tooltip>
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
      </Paper>

      {/* Data Table */}
      <Paper>
        <TableContainer>
          {viewMode === 'list' ? (
            // List View - Shows all variants
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Full SKU</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Parent UPIS-H</TableCell>
                  <TableCell>Color</TableCell>
                  <TableCell>Condition</TableCell>
                  <TableCell>Zoho Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      Loading...
                    </TableCell>
                  </TableRow>
                ) : paginatedListData.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      No items found
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedListData.map((variant) => (
                    <TableRow key={variant.id} hover>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {variant.full_sku}
                        </Typography>
                      </TableCell>
                      <TableCell>{variant.identity?.family?.base_name || '-'}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={getTypeLabel(variant.identity?.type || 'Product')}
                          color={getTypeColor(variant.identity?.type || 'Product')}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontFamily="monospace">
                          {variant.identity?.generated_upis_h || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>{variant.color_code || '-'}</TableCell>
                      <TableCell>{variant.condition_code || 'U'}</TableCell>
                      <TableCell>{getSyncStatusChip(variant.zoho_sync_status)}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          ) : (
            // Grouped View - Shows grouped by parent UPIS-H
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell width={50} />
                  <TableCell>Parent UPIS-H</TableCell>
                  <TableCell>Name</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Brand</TableCell>
                  <TableCell>Variants</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      Loading...
                    </TableCell>
                  </TableRow>
                ) : paginatedGroupedData.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      No items found
                    </TableCell>
                  </TableRow>
                ) : (
                  paginatedGroupedData.map((group) => (
                    <>
                      <TableRow
                        key={group.parent_upis_h}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => handleToggleExpand(group.parent_upis_h)}
                      >
                        <TableCell>
                          <IconButton size="small">
                            {expandedRows.has(group.parent_upis_h) ? (
                              <ExpandLess />
                            ) : (
                              <ExpandMore />
                            )}
                          </IconButton>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" fontFamily="monospace">
                            {group.parent_upis_h}
                          </Typography>
                        </TableCell>
                        <TableCell>{group.name}</TableCell>
                        <TableCell>
                          <Chip
                            size="small"
                            label={getTypeLabel(group.type)}
                            color={getTypeColor(group.type)}
                          />
                        </TableCell>
                        <TableCell>{group.brand || '-'}</TableCell>
                        <TableCell>
                          <Chip size="small" label={`${group.alias_count} variant(s)`} />
                        </TableCell>
                      </TableRow>
                      {expandedRows.has(group.parent_upis_h) && (
                        <ExpandedRow
                          parentUpisH={group.parent_upis_h}
                          variants={group.variants}
                        />
                      )}
                    </>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={viewMode === 'list' ? filteredVariants.length : groupedData.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      {/* Create Product Dialog */}
      <CreateProductDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
      />
    </Box>
  )
}
