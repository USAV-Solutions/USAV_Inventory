import { Box, Grid, Card, CardContent, Typography, Button } from '@mui/material'
import {
  QrCodeScanner,
  Search,
  Category,
  Inventory,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'

interface QuickAction {
  title: string
  description: string
  path: string
  icon: React.ReactNode
  color: string
  roles: ('ADMIN' | 'WAREHOUSE_OP' | 'SALES_REP')[]
}

const quickActions: QuickAction[] = [
  {
    title: 'Scan Tool',
    description: 'Receive, move, or audit inventory items',
    path: '/warehouse/ops',
    icon: <QrCodeScanner sx={{ fontSize: 48 }} />,
    color: '#1976d2',
    roles: ['ADMIN', 'WAREHOUSE_OP'],
  },
  {
    title: 'Stock Lookup',
    description: 'Search inventory by SKU or serial number',
    path: '/warehouse/lookup',
    icon: <Search sx={{ fontSize: 48 }} />,
    color: '#2e7d32',
    roles: ['ADMIN', 'WAREHOUSE_OP'],
  },
  {
    title: 'Product Identities',
    description: 'Manage product families and identities',
    path: '/catalog/identities',
    icon: <Category sx={{ fontSize: 48 }} />,
    color: '#ed6c02',
    roles: ['ADMIN', 'SALES_REP'],
  },
  {
    title: 'Variant Manager',
    description: 'Manage variants and Zoho sync status',
    path: '/catalog/variants',
    icon: <Inventory sx={{ fontSize: 48 }} />,
    color: '#9c27b0',
    roles: ['ADMIN', 'SALES_REP'],
  },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { user, hasRole } = useAuth()

  const filteredActions = quickActions.filter((action) =>
    hasRole(action.roles)
  )

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome, {user?.username}!
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Role: {user?.role}
      </Typography>

      <Typography variant="h6" gutterBottom>
        Quick Actions
      </Typography>
      <Grid container spacing={3}>
        {filteredActions.map((action) => (
          <Grid item xs={12} sm={6} md={3} key={action.path}>
            <Card
              sx={{
                height: '100%',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
              onClick={() => navigate(action.path)}
            >
              <CardContent
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 3,
                }}
              >
                <Box sx={{ color: action.color, mb: 2 }}>{action.icon}</Box>
                <Typography variant="h6" gutterBottom>
                  {action.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {action.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  )
}
