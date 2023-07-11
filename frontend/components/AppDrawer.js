import {
  Drawer,
  Toolbar,
  Box,
  Divider,
  Slide
} from '@mui/material'

import TemplatesList from './TemplatesList'
import EnvironsList from './EnvironsList'
import useProject from '../api/useProject'
import DataList from './DataList'

const drawerWidth = 240

const AppDrawer = () => {
  const mainMenu = useProject(state => state.mainMenu)

  return (
    <Drawer
      variant='permanent'
      sx={{
        overflow: 'hidden',
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          boxSizing: 'border-box',
          width: drawerWidth,
          overflow: 'hidden'
        }
      }}
    >
      <Toolbar variant='dense' />
      <Slide direction='down' in={mainMenu} mountOnEnter unmountOnExit>
        <Box sx={{ overflow: 'auto' }}>
          <TemplatesList />
          <Divider />
          <EnvironsList />
        </Box>
      </Slide>
      <Slide direction='up' in={!mainMenu} mountOnEnter unmountOnExit>
        <Box sx={{ overflow: 'auto' }}>
          <DataList />
        </Box>
      </Slide>
    </Drawer>
  )
}

export default AppDrawer
