import {
  Routes,
  Route,
  Outlet
} from 'react-router-dom'
import {
  Box,
  Container,
  Toolbar
} from '@mui/material'

import AppDrawer from "~/components/AppDrawer"
import DataSettings from '~/features/data_settings/components/DataSettings'

const BaseLayout = () => {
  return (
    <Box sx={{ display: 'flex' }}>
      <AppDrawer />
      <Container>
        <Toolbar sx={{ mb: 2 }} />
        <Outlet />
      </Container>
    </Box>
  )
}

const AppRoutes = () => {

  return (
    <Routes>
      <Route path='/' element={<BaseLayout />}>
        <Route path='/add_template' element={<p>Add Template</p>} />
        <Route path='/add_environ' element={<p>Add Environ</p>} />
        <Route path='/templates/:id' element={<Outlet />}>
          <Route path='_init' element={<DataSettings />} />
          <Route path=':instance/:tableName' element={<p>editor</p>} />
        </Route>
      </Route>
    </Routes>
  )
}

export default AppRoutes
