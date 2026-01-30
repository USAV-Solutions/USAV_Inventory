import { useState } from 'react'
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
  Typography,
  Divider,
  Autocomplete,
  List,
  ListItem,
  ListItemText,
  Chip,
  Grid,
  InputAdornment,
  CircularProgress,
  Paper,
} from '@mui/material'
import { Add, Search } from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axiosClient from '../../api/axiosClient'
import { CATALOG, LOOKUPS } from '../../api/endpoints'
import {
  Brand,
  Color,
  Condition,
  LCIDefinition,
  ProductIdentity,
} from '../../types/inventory'

interface CreateProductDialogProps {
  open: boolean
  onClose: () => void
}

type ItemType = 'Product' | 'P' | 'B' | 'K'

const typeOptions: { value: ItemType; label: string; description: string }[] = [
  { value: 'Product', label: 'Product', description: 'A standard sellable product' },
  { value: 'P', label: 'Part', description: 'A component part of a product' },
  { value: 'B', label: 'Bundle', description: 'A collection of products sold together' },
  { value: 'K', label: 'Kit', description: 'A kit with included items' },
]

export default function CreateProductDialog({ open, onClose }: CreateProductDialogProps) {
  const queryClient = useQueryClient()
  
  // Form state
  const [itemType, setItemType] = useState<ItemType>('Product')
  const [name, setName] = useState('')
  const [dimensionLength, setDimensionLength] = useState('')
  const [dimensionWidth, setDimensionWidth] = useState('')
  const [dimensionHeight, setDimensionHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null)
  const [selectedColor, setSelectedColor] = useState<Color | null>(null)
  const [selectedCondition, setSelectedCondition] = useState<Condition | null>(null)
  const [newBrandName, setNewBrandName] = useState('')
  const [newColorName, setNewColorName] = useState('')
  const [newColorCode, setNewColorCode] = useState('')
  const [newConditionName, setNewConditionName] = useState('')
  const [newConditionCode, setNewConditionCode] = useState('')
  
  // Bundle-specific
  const [bundleComponents, setBundleComponents] = useState<ProductIdentity[]>([])
  const [componentSearchQuery, setComponentSearchQuery] = useState('')
  
  // Kit-specific
  const [kitIncludedProducts, setKitIncludedProducts] = useState('')
  
  // Part-specific
  const [selectedParentProduct, setSelectedParentProduct] = useState<ProductIdentity | null>(null)
  const [selectedLCI, setSelectedLCI] = useState<LCIDefinition | null>(null)
  const [newLCIComponentName, setNewLCIComponentName] = useState('')

  // Fetch lookups
  const { data: brandsData } = useQuery({
    queryKey: ['brands'],
    queryFn: async () => {
      const response = await axiosClient.get(LOOKUPS.BRANDS, { params: { limit: 1000 } })
      return response.data.items || []
    },
    enabled: open,
  })

  const { data: colorsData } = useQuery({
    queryKey: ['colors'],
    queryFn: async () => {
      const response = await axiosClient.get(LOOKUPS.COLORS, { params: { limit: 1000 } })
      return response.data.items || []
    },
    enabled: open,
  })

  const { data: conditionsData } = useQuery({
    queryKey: ['conditions'],
    queryFn: async () => {
      const response = await axiosClient.get(LOOKUPS.CONDITIONS, { params: { limit: 1000 } })
      return response.data.items || []
    },
    enabled: open,
  })

  const { data: identitiesData } = useQuery({
    queryKey: ['identities'],
    queryFn: async () => {
      const response = await axiosClient.get(CATALOG.IDENTITIES, { params: { limit: 1000 } })
      return response.data.items || []
    },
    enabled: open,
  })

  // Fetch LCI definitions for selected parent product
  const { data: lciData } = useQuery({
    queryKey: ['lci-definitions', selectedParentProduct?.product_id],
    queryFn: async () => {
      if (!selectedParentProduct) return []
      const response = await axiosClient.get(LOOKUPS.LCI_DEFINITIONS, {
        params: { product_id: selectedParentProduct.product_id, limit: 100 }
      })
      return response.data.items || []
    },
    enabled: open && itemType === 'P' && !!selectedParentProduct,
  })

  // Mutations
  const createBrandMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await axiosClient.post(LOOKUPS.BRANDS, { name })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['brands'] })
      setSelectedBrand(data)
      setNewBrandName('')
    },
  })

  const createColorMutation = useMutation({
    mutationFn: async ({ name, code }: { name: string; code: string }) => {
      const response = await axiosClient.post(LOOKUPS.COLORS, { name, code })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['colors'] })
      setSelectedColor(data)
      setNewColorName('')
      setNewColorCode('')
    },
  })

  const createConditionMutation = useMutation({
    mutationFn: async ({ name, code }: { name: string; code: string }) => {
      const response = await axiosClient.post(LOOKUPS.CONDITIONS, { name, code })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['conditions'] })
      setSelectedCondition(data)
      setNewConditionName('')
      setNewConditionCode('')
    },
  })

  const createLCIMutation = useMutation({
    mutationFn: async ({ product_id, component_name }: { product_id: number; component_name: string }) => {
      const response = await axiosClient.post(LOOKUPS.LCI_DEFINITIONS, { product_id, component_name })
      return response.data
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['lci-definitions', selectedParentProduct?.product_id] })
      setSelectedLCI(data)
      setNewLCIComponentName('')
    },
  })

  const createProductMutation = useMutation({
    mutationFn: async (data: any) => {
      // First create the family
      const familyResponse = await axiosClient.post(CATALOG.FAMILIES, {
        base_name: data.name,
        brand_id: data.brand_id,
        dimension_length: data.dimension_length,
        dimension_width: data.dimension_width,
        dimension_height: data.dimension_height,
        weight: data.weight,
        kit_included_products: data.kit_included_products,
      })
      
      // Then create the identity
      const identityResponse = await axiosClient.post(CATALOG.IDENTITIES, {
        product_id: familyResponse.data.product_id,
        type: data.type,
        lci: data.lci,
      })
      
      // Then create the variant if color/condition provided
      if (data.color_code || data.condition_code) {
        await axiosClient.post(CATALOG.VARIANTS, {
          identity_id: identityResponse.data.id,
          color_code: data.color_code,
          condition_code: data.condition_code,
        })
      }
      
      // If bundle, add components
      if (data.type === 'B' && data.component_ids?.length > 0) {
        for (const componentId of data.component_ids) {
          await axiosClient.post(CATALOG.BUNDLES, {
            parent_identity_id: identityResponse.data.id,
            child_identity_id: componentId,
            quantity_required: 1,
            role: 'Primary',
          })
        }
      }
      
      return identityResponse.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['variants'] })
      queryClient.invalidateQueries({ queryKey: ['identities'] })
      queryClient.invalidateQueries({ queryKey: ['families'] })
      handleClose()
    },
  })

  const handleClose = () => {
    // Reset form
    setItemType('Product')
    setName('')
    setDimensionLength('')
    setDimensionWidth('')
    setDimensionHeight('')
    setWeight('')
    setSelectedBrand(null)
    setSelectedColor(null)
    setSelectedCondition(null)
    setBundleComponents([])
    setKitIncludedProducts('')
    setSelectedParentProduct(null)
    setSelectedLCI(null)
    onClose()
  }

  const handleSubmit = () => {
    const data: any = {
      type: itemType,
      name,
      brand_id: selectedBrand?.id,
      dimension_length: dimensionLength ? parseFloat(dimensionLength) : undefined,
      dimension_width: dimensionWidth ? parseFloat(dimensionWidth) : undefined,
      dimension_height: dimensionHeight ? parseFloat(dimensionHeight) : undefined,
      weight: weight ? parseFloat(weight) : undefined,
    }
    
    // Type-specific fields
    if (itemType !== 'B') {
      data.color_code = selectedColor?.code
      data.condition_code = selectedCondition?.code
    }
    
    if (itemType === 'B') {
      data.component_ids = bundleComponents.map((c) => c.id)
    }
    
    if (itemType === 'K') {
      data.kit_included_products = kitIncludedProducts
    }
    
    if (itemType === 'P') {
      data.lci = selectedLCI?.lci_index
    }
    
    createProductMutation.mutate(data)
  }

  const handleAddBrand = () => {
    if (newBrandName.trim()) {
      createBrandMutation.mutate(newBrandName.trim())
    }
  }

  const handleAddColor = () => {
    if (newColorName.trim() && newColorCode.trim()) {
      createColorMutation.mutate({
        name: newColorName.trim(),
        code: newColorCode.trim().toUpperCase(),
      })
    }
  }

  const handleAddCondition = () => {
    if (newConditionName.trim() && newConditionCode.trim()) {
      createConditionMutation.mutate({
        name: newConditionName.trim(),
        code: newConditionCode.trim().toUpperCase(),
      })
    }
  }

  const handleAddLCI = () => {
    if (selectedParentProduct && newLCIComponentName.trim()) {
      createLCIMutation.mutate({
        product_id: selectedParentProduct.product_id,
        component_name: newLCIComponentName.trim(),
      })
    }
  }

  const handleAddBundleComponent = (identity: ProductIdentity) => {
    if (!bundleComponents.find((c) => c.id === identity.id)) {
      setBundleComponents([...bundleComponents, identity])
    }
    setComponentSearchQuery('')
  }

  const handleRemoveBundleComponent = (id: number) => {
    setBundleComponents(bundleComponents.filter((c) => c.id !== id))
  }

  // Filter identities for component search
  const filteredIdentities = (identitiesData || []).filter((identity: ProductIdentity) => {
    if (!componentSearchQuery.trim()) return false
    const query = componentSearchQuery.toLowerCase()
    return identity.generated_upis_h?.toLowerCase().includes(query)
  })

  // Filter parent products (only Products, not Parts or Bundles)
  const parentProductOptions = (identitiesData || []).filter(
    (identity: ProductIdentity) => identity.type === 'Product'
  )

  const isValid = name.trim().length > 0 && (
    itemType !== 'B' || bundleComponents.length > 0
  ) && (
    itemType !== 'P' || (selectedParentProduct && selectedLCI)
  )

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>Add New Item</DialogTitle>
      <DialogContent>
        <Box sx={{ mt: 2 }}>
          {/* Type Selection */}
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Type *</InputLabel>
            <Select
              value={itemType}
              label="Type *"
              onChange={(e) => setItemType(e.target.value as ItemType)}
            >
              {typeOptions.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  <Box>
                    <Typography variant="body1">{option.label}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {option.description}
                    </Typography>
                  </Box>
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Divider sx={{ mb: 3 }} />

          {/* Common Fields */}
          <Typography variant="subtitle2" sx={{ mb: 2 }}>
            Basic Information
          </Typography>
          
          <TextField
            fullWidth
            label="Name *"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter product name (e.g., 'Bose 201 Series IV Speaker')"
            sx={{ mb: 2 }}
          />

          {/* Brand Selection */}
          <Box sx={{ mb: 2 }}>
            <Autocomplete
              options={brandsData || []}
              getOptionLabel={(option: Brand) => option.name}
              value={selectedBrand}
              onChange={(_, value) => setSelectedBrand(value)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Brand / Manufacturer"
                  placeholder="Search or add a brand..."
                />
              )}
              renderOption={(props, option) => (
                <li {...props} key={option.id}>
                  {option.name}
                </li>
              )}
            />
            <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
              <TextField
                size="small"
                placeholder="New brand name"
                value={newBrandName}
                onChange={(e) => setNewBrandName(e.target.value)}
                sx={{ flexGrow: 1 }}
              />
              <Button
                size="small"
                variant="outlined"
                startIcon={<Add />}
                onClick={handleAddBrand}
                disabled={!newBrandName.trim() || createBrandMutation.isPending}
              >
                Add
              </Button>
            </Box>
          </Box>

          {/* Dimensions */}
          <Typography variant="subtitle2" sx={{ mb: 2, mt: 3 }}>
            Dimensions & Weight
          </Typography>
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Length"
                type="number"
                value={dimensionLength}
                onChange={(e) => setDimensionLength(e.target.value)}
                InputProps={{
                  endAdornment: <InputAdornment position="end">in</InputAdornment>,
                }}
                placeholder="0.00"
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Width"
                type="number"
                value={dimensionWidth}
                onChange={(e) => setDimensionWidth(e.target.value)}
                InputProps={{
                  endAdornment: <InputAdornment position="end">in</InputAdornment>,
                }}
                placeholder="0.00"
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Height"
                type="number"
                value={dimensionHeight}
                onChange={(e) => setDimensionHeight(e.target.value)}
                InputProps={{
                  endAdornment: <InputAdornment position="end">in</InputAdornment>,
                }}
                placeholder="0.00"
              />
            </Grid>
          </Grid>
          <TextField
            fullWidth
            label="Weight"
            type="number"
            value={weight}
            onChange={(e) => setWeight(e.target.value)}
            InputProps={{
              endAdornment: <InputAdornment position="end">lb</InputAdornment>,
            }}
            placeholder="0.00"
            sx={{ mb: 3 }}
          />

          <Divider sx={{ mb: 3 }} />

          {/* Color & Condition - Not for Bundles */}
          {itemType !== 'B' && (
            <>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Variant Options
              </Typography>
              
              {/* Color */}
              <Box sx={{ mb: 2 }}>
                <Autocomplete
                  options={colorsData || []}
                  getOptionLabel={(option: Color) => `${option.name} - ${option.code}`}
                  value={selectedColor}
                  onChange={(_, value) => setSelectedColor(value)}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Color"
                      placeholder="Select or add a color..."
                    />
                  )}
                  renderOption={(props, option) => (
                    <li {...props} key={option.id}>
                      {option.name} - {option.code}
                    </li>
                  )}
                />
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <TextField
                    size="small"
                    placeholder="Color name"
                    value={newColorName}
                    onChange={(e) => setNewColorName(e.target.value)}
                    sx={{ flexGrow: 1 }}
                  />
                  <TextField
                    size="small"
                    placeholder="Code (2 chars)"
                    value={newColorCode}
                    onChange={(e) => setNewColorCode(e.target.value.slice(0, 2))}
                    sx={{ width: 100 }}
                  />
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={handleAddColor}
                    disabled={!newColorName.trim() || !newColorCode.trim() || createColorMutation.isPending}
                  >
                    Add
                  </Button>
                </Box>
              </Box>

              {/* Condition */}
              <Box sx={{ mb: 3 }}>
                <Autocomplete
                  options={conditionsData || []}
                  getOptionLabel={(option: Condition) => `${option.name} - ${option.code}`}
                  value={selectedCondition}
                  onChange={(_, value) => setSelectedCondition(value)}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Condition"
                      placeholder="Select or add a condition..."
                    />
                  )}
                  renderOption={(props, option) => (
                    <li {...props} key={option.id}>
                      {option.name} - {option.code}
                    </li>
                  )}
                />
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                  <TextField
                    size="small"
                    placeholder="Condition name"
                    value={newConditionName}
                    onChange={(e) => setNewConditionName(e.target.value)}
                    sx={{ flexGrow: 1 }}
                  />
                  <TextField
                    size="small"
                    placeholder="Code (1 char)"
                    value={newConditionCode}
                    onChange={(e) => setNewConditionCode(e.target.value.slice(0, 1))}
                    sx={{ width: 100 }}
                  />
                  <Button
                    size="small"
                    variant="outlined"
                    startIcon={<Add />}
                    onClick={handleAddCondition}
                    disabled={!newConditionName.trim() || !newConditionCode.trim() || createConditionMutation.isPending}
                  >
                    Add
                  </Button>
                </Box>
              </Box>

              <Divider sx={{ mb: 3 }} />
            </>
          )}

          {/* Bundle-specific: Component SKUs */}
          {itemType === 'B' && (
            <>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Bundle Components *
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Search and add existing products to include in this bundle. Components must already exist in the system.
              </Typography>
              
              <TextField
                fullWidth
                label="Search Components by UPIS-H"
                value={componentSearchQuery}
                onChange={(e) => setComponentSearchQuery(e.target.value)}
                placeholder="Type to search (e.g., '00845')"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Search />
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 1 }}
              />
              
              {filteredIdentities.length > 0 && (
                <Paper variant="outlined" sx={{ mb: 2, maxHeight: 200, overflow: 'auto' }}>
                  <List dense>
                    {filteredIdentities.slice(0, 10).map((identity: ProductIdentity) => (
                      <ListItem
                        key={identity.id}
                        button
                        onClick={() => handleAddBundleComponent(identity)}
                        disabled={bundleComponents.some((c) => c.id === identity.id)}
                      >
                        <ListItemText
                          primary={identity.generated_upis_h}
                          secondary={`Type: ${identity.type}`}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              )}
              
              {bundleComponents.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="caption" color="text.secondary">
                    Selected Components:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                    {bundleComponents.map((component) => (
                      <Chip
                        key={component.id}
                        label={component.generated_upis_h}
                        onDelete={() => handleRemoveBundleComponent(component.id)}
                      />
                    ))}
                  </Box>
                </Box>
              )}
              
              <Divider sx={{ mb: 3 }} />
            </>
          )}

          {/* Kit-specific: Included Products */}
          {itemType === 'K' && (
            <>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Included Products
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                List the products included in this kit (free-form text).
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Included Products"
                value={kitIncludedProducts}
                onChange={(e) => setKitIncludedProducts(e.target.value)}
                placeholder="e.g., Speaker unit, Remote control, Power cable, User manual"
                sx={{ mb: 3 }}
              />
              <Divider sx={{ mb: 3 }} />
            </>
          )}

          {/* Part-specific: Parent SKU and LCI */}
          {itemType === 'P' && (
            <>
              <Typography variant="subtitle2" sx={{ mb: 2 }}>
                Part Configuration *
              </Typography>
              
              {/* Parent Product */}
              <Autocomplete
                options={parentProductOptions}
                getOptionLabel={(option: ProductIdentity) => 
                  `${option.generated_upis_h} - ${option.product_id}`
                }
                value={selectedParentProduct}
                onChange={(_, value) => {
                  setSelectedParentProduct(value)
                  setSelectedLCI(null)
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Parent Product *"
                    placeholder="Select the parent product this part belongs to..."
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props} key={option.id}>
                    <Box>
                      <Typography variant="body2">{option.generated_upis_h}</Typography>
                    </Box>
                  </li>
                )}
                sx={{ mb: 2 }}
              />
              
              {selectedParentProduct && (
                <>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Parent Name: {selectedParentProduct.product_id}
                  </Typography>
                  
                  {/* LCI Selection */}
                  <Box sx={{ mb: 2 }}>
                    <Autocomplete
                      options={lciData || []}
                      getOptionLabel={(option: LCIDefinition) => 
                        `${option.lci_index} - ${option.component_name}`
                      }
                      value={selectedLCI}
                      onChange={(_, value) => setSelectedLCI(value)}
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Local Component Index (LCI) *"
                          placeholder="Select or add a component index..."
                        />
                      )}
                      renderOption={(props, option) => (
                        <li {...props} key={option.id}>
                          {option.lci_index} - {option.component_name}
                        </li>
                      )}
                    />
                    <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                      <TextField
                        size="small"
                        placeholder="Component name (e.g., Motherboard)"
                        value={newLCIComponentName}
                        onChange={(e) => setNewLCIComponentName(e.target.value)}
                        sx={{ flexGrow: 1 }}
                      />
                      <Button
                        size="small"
                        variant="outlined"
                        startIcon={<Add />}
                        onClick={handleAddLCI}
                        disabled={!newLCIComponentName.trim() || createLCIMutation.isPending}
                      >
                        Add LCI
                      </Button>
                    </Box>
                    <Typography variant="caption" color="text.secondary">
                      LCI index will be auto-generated
                    </Typography>
                  </Box>
                </>
              )}
              
              <Divider sx={{ mb: 3 }} />
            </>
          )}

          {/* SKU Preview */}
          <Box sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>
              SKU Preview
            </Typography>
            <Typography variant="body2" color="text.secondary">
              SKU will be auto-generated based on the input fields. Format: {'{product_id}-{type}-{lci}-{color}-{condition}'}
            </Typography>
          </Box>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={handleSubmit}
          disabled={!isValid || createProductMutation.isPending}
        >
          {createProductMutation.isPending ? <CircularProgress size={24} /> : 'Create'}
        </Button>
      </DialogActions>
    </Dialog>
  )
}
