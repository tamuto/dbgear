import { FC, useEffect } from 'react'
import { Outlet } from 'react-router-dom'
import {
  Box,
  Container
} from '@mui/material'

import LocationHandler from './LocationHandler'
import useProject from '../api/useProject'
import AppDrawer from './AppDrawer'

const BaseLayout: FC = () => {
  // FIXME ScrollTopをどうするか？
  const updateProjectInfo = useProject(state => state.updateProjectInfo)
  const updateEnvirons = useProject(state => state.updateEnvirons)

  useEffect(() => {
    updateProjectInfo()
    updateEnvirons()
  }, [])

  return (
    <LocationHandler>
      <Box sx={{ display: 'flex' }}>
        <AppDrawer />
        <Container sx={{ py: 2 }}>
          <Outlet />
        </Container>
      </Box>
    </LocationHandler>
  )
}

export default BaseLayout
