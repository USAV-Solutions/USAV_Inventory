import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import { UserRole } from '../../types/auth'
import { Box, CircularProgress } from '@mui/material'

interface RoleGuardProps {
  allowedRoles: UserRole[]
  children?: React.ReactNode
}

export default function RoleGuard({ allowedRoles, children }: RoleGuardProps) {
  const { isAuthenticated, isLoading, hasRole } = useAuth()

  if (isLoading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (!hasRole(allowedRoles)) {
    return <Navigate to="/" replace />
  }

  return children ? <>{children}</> : <Outlet />
}
