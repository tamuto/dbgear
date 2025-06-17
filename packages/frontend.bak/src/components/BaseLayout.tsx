import { FC } from 'react'
import { Outlet, ScrollRestoration } from 'react-router-dom'
import {
  Box,
  Container
} from '@mui/material'

import LocationHandler from '~/cmp/LocationHandler'
import AppDrawer from '~/cmp/AppDrawer'
import GlobalCss from '~/cmp/GlobalCss'

const BaseLayout: FC = () => {
  return (
    <LocationHandler>
      <ScrollRestoration />
      <Box sx={{ display: 'flex' }}>
        <AppDrawer />
        <Container sx={{ py: 2 }} css={GlobalCss} >
          <Outlet />
        </Container>
      </Box>
    </LocationHandler>
  )
}

export default BaseLayout
