import {
  Routes,
  Route,
  Outlet
} from 'react-router-dom'
import {
  Box,
  Container,
} from '@mui/material'

import AppDrawer from "~/components/AppDrawer"
import TemplateDataSettings from '~/features/template_data_settings/components/TemplateDataSettings'
import TemplateDataTab from '~/features/template_data_tab/components/TemplateDataTab'
import TemplateDataEditor from '../features/template_data_tab/components/TemplateDataEditor'

const BaseLayout = () => {
  return (
    <Box sx={{ display: 'flex' }}>
      <AppDrawer />
      <Container sx={{ pt: 2, pb: 2 }}>
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
        <Route path='/templates/:id' element={<Outlet context={{ data: undefined, initData: () => {} }} />}>
          <Route path='_init' element={<TemplateDataSettings />} />
          <Route path=':instance/:tableName' element={<TemplateDataTab />}>
            <Route path='_data' element={<TemplateDataEditor />} />
            <Route path='_props' element={<TemplateDataSettings />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  )
}

export default AppRoutes
