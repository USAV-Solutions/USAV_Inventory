import { useState, useRef, useEffect } from 'react'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Typography,
  ToggleButton,
  ToggleButtonGroup,
  Alert,
  Snackbar,
  Paper,
  Chip,
} from '@mui/material'
import {
  LocalShipping,
  MoveUp,
  FactCheck,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material'
import axiosClient from '../api/axiosClient'

type Mode = 'receive' | 'move' | 'audit'

interface ItemInfo {
  serial_number: string
  sku: string
  location: string
  status: string
}

export default function WarehouseOps() {
  const [mode, setMode] = useState<Mode>('move')
  const [input, setInput] = useState('')
  const [itemInfo, setItemInfo] = useState<ItemInfo | null>(null)
  const [waitingForLocation, setWaitingForLocation] = useState(false)
  const [notification, setNotification] = useState<{
    open: boolean
    message: string
    severity: 'success' | 'error'
  }>({ open: false, message: '', severity: 'success' })
  
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-focus the input field
  useEffect(() => {
    inputRef.current?.focus()
  }, [mode])

  const showNotification = (message: string, severity: 'success' | 'error') => {
    setNotification({ open: true, message, severity })
    // Play sound based on severity
    if (severity === 'success') {
      // Could add a success beep
    }
  }

  const handleModeChange = (_: React.MouseEvent<HTMLElement>, newMode: Mode | null) => {
    if (newMode) {
      setMode(newMode)
      setItemInfo(null)
      setWaitingForLocation(false)
      setInput('')
    }
  }

  const handleInputKeyDown = async (e: React.KeyboardEvent) => {
    if (e.key !== 'Enter' || !input.trim()) return

    const scannedValue = input.trim()
    setInput('')

    try {
      switch (mode) {
        case 'receive':
          await handleReceive(scannedValue)
          break
        case 'move':
          await handleMove(scannedValue)
          break
        case 'audit':
          await handleAudit(scannedValue)
          break
      }
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Operation failed'
      showNotification(message, 'error')
      setItemInfo(null)
      setWaitingForLocation(false)
    }

    inputRef.current?.focus()
  }

  const handleReceive = async (serialNumber: string) => {
    await axiosClient.post('/inventory/receive', { serial_number: serialNumber })
    showNotification(`Item ${serialNumber} received successfully!`, 'success')
  }

  const handleMove = async (scannedValue: string) => {
    if (!waitingForLocation) {
      // First scan - get item info
      const response = await axiosClient.get(`/inventory/audit/${scannedValue}`)
      const item = response.data.items?.[0]
      if (item) {
        setItemInfo({
          serial_number: item.serial_number,
          sku: scannedValue,
          location: item.location_code,
          status: item.status,
        })
        setWaitingForLocation(true)
      }
    } else {
      // Second scan - move to location
      await axiosClient.post('/inventory/move', {
        serial_number: itemInfo?.serial_number,
        new_location: scannedValue,
      })
      showNotification(
        `Moved ${itemInfo?.serial_number} to ${scannedValue}`,
        'success'
      )
      setItemInfo(null)
      setWaitingForLocation(false)
    }
  }

  const handleAudit = async (sku: string) => {
    const response = await axiosClient.get(`/inventory/audit/${sku}`)
    const item = response.data.items?.[0]
    if (item) {
      setItemInfo({
        serial_number: item.serial_number,
        sku: sku,
        location: item.location_code,
        status: item.status,
      })
    }
  }

  const getModeLabel = () => {
    switch (mode) {
      case 'receive':
        return 'Scan item barcode to receive'
      case 'move':
        return waitingForLocation
          ? 'Now scan destination LOCATION'
          : 'Scan item barcode to move'
      case 'audit':
        return 'Scan SKU to view stock info'
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Warehouse Operations
      </Typography>

      {/* Mode Toggle */}
      <ToggleButtonGroup
        value={mode}
        exclusive
        onChange={handleModeChange}
        sx={{ mb: 3 }}
      >
        <ToggleButton value="receive" size="large">
          <LocalShipping sx={{ mr: 1 }} /> Receive
        </ToggleButton>
        <ToggleButton value="move" size="large">
          <MoveUp sx={{ mr: 1 }} /> Move
        </ToggleButton>
        <ToggleButton value="audit" size="large">
          <FactCheck sx={{ mr: 1 }} /> Audit
        </ToggleButton>
      </ToggleButtonGroup>

      {/* Scanner Input */}
      <Paper
        sx={{
          p: 3,
          mb: 3,
          bgcolor: waitingForLocation ? 'warning.light' : 'background.paper',
        }}
      >
        <Typography variant="h6" gutterBottom>
          {getModeLabel()}
        </Typography>
        <TextField
          inputRef={inputRef}
          fullWidth
          variant="outlined"
          placeholder="Scan barcode here..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleInputKeyDown}
          autoFocus
          sx={{
            '& .MuiOutlinedInput-root': {
              fontSize: '1.5rem',
            },
          }}
        />
      </Paper>

      {/* Item Info Card */}
      {itemInfo && (
        <Card sx={{ bgcolor: 'success.light' }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Item Found
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Chip label={`Serial: ${itemInfo.serial_number}`} variant="outlined" />
              <Chip label={`SKU: ${itemInfo.sku}`} variant="outlined" />
              <Chip label={`Location: ${itemInfo.location}`} variant="outlined" />
              <Chip
                label={itemInfo.status}
                color={itemInfo.status === 'IN_STOCK' ? 'success' : 'warning'}
              />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Notification Snackbar */}
      <Snackbar
        open={notification.open}
        autoHideDuration={4000}
        onClose={() => setNotification((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert
          severity={notification.severity}
          icon={notification.severity === 'success' ? <CheckCircle /> : <ErrorIcon />}
          sx={{ fontSize: '1.2rem' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}
