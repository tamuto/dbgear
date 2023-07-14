import {
  Routes,
  Route,
  Outlet
} from 'react-router-dom'

import DataSettings from '~/features/data_settings/components/DataSettings'

const AppRoutes = () => {

  return (
    <Routes>
      <Route path='/' element={<div />} />
      <Route path='/add_template' element={<p>Add Template</p>} />
      <Route path='/add_environ' element={<p>Add Environ</p>} />
      <Route path='/templates/:id' element={<Outlet />}>
        <Route path='_init' element={<DataSettings />} />
      </Route>
    </Routes>
  )
}

export default AppRoutes
