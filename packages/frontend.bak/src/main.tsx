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
import { useTranslation } from 'react-i18next'
import { initIn4UILib } from '@infodb/uilib'

import routes from './routes'
import theme from './theme'

import './resources/i18n/configs'

const router = createHashRouter(routes)

const App = () => {
  const { t } = useTranslation()
  initIn4UILib({
    requiredLabel: t('caption.required'),
  })

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
