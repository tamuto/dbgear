import { useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import {
  HashRouter,
  Routes,
  Route,
  Outlet
} from 'react-router-dom'
import {
  createTheme,
  ThemeProvider,
  CssBaseline,
  Container,
  Toolbar,
  Box
} from '@mui/material'

import ScrollTop from 'github://tamuto/uilib/components/misc/ScrollTop.js'

import AppNavigate from '~/components/AppNavigate'
import AppDrawer from "~/components/AppDrawer"
import LocationHandler from '~/components/LocationHandler'

import useProject from '~/api/useProject'

import res from '~/resources/theme.json'

const theme = createTheme(res)

const App = () => {
  const updateProjectInfo = useProject(state => state.updateProjectInfo)

  useEffect(() => {
    updateProjectInfo()
  }, [])

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <HashRouter>
        <LocationHandler>
          <ScrollTop />
          <AppNavigate />
          <Box sx={{ display: 'flex' }}>
            <AppDrawer />
            <Container>
              <Toolbar />
              <Routes>
                <Route path='/' element={<div />} />
                <Route path='/add_template' element={<p>Add Template</p>} />
                <Route path='/add_environ' element={<p>Add Environ</p>} />
                <Route path='/templates/:name' element={<Outlet />}>
                  <Route path='_init' element={<p>init data</p>} />
                </Route>
              </Routes>
            </Container>
          </Box>
        </LocationHandler>
      </HashRouter>
    </ThemeProvider>
  )
}

const root = createRoot(document.getElementById('app'))
root.render(
  <App />
)
