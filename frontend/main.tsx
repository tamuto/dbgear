import { createRoot } from 'react-dom/client'
import {
  createHashRouter,
  RouterProvider
} from 'react-router-dom'
import {
  ThemeProvider,
  CssBaseline
} from '@mui/material'
import { SnackbarProvider } from 'notistack'

import routes from './routes'
import theme from './theme'

const router = createHashRouter(routes)

const App = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <SnackbarProvider>
        <RouterProvider router={router} />
      </SnackbarProvider>
    </ThemeProvider>
  )
}

const root = createRoot(document.getElementById("app") as HTMLElement)
root.render(<App />)
