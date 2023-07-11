import {
  AppBar,
  Toolbar,
  Typography,
  Breadcrumbs,
  Link
} from '@mui/material'

import NavigateNextIcon from '@mui/icons-material/NavigateNext'

import useProject from '~/api/useProject'

const AppNavigate = () => {
  const routePath = useProject(state => state.routePath)

  return (
    <AppBar position='fixed' sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar variant='dense'>
        <Typography component='div' sx={{ mr: 1 }}>DB Gear</Typography>
        <Typography component='div' sx={{ mr: 1 }}>@</Typography>
        <Breadcrumbs separator={<NavigateNextIcon fontSize='small' />} sx={{ color: 'white' }}>
          {
            routePath.map(item => (
              <Link key={item} color='primary.contrastText' underline='hover'>{item}</Link>
            ))
          }
        </Breadcrumbs>
      </Toolbar>
    </AppBar>
  )
}

export default AppNavigate
