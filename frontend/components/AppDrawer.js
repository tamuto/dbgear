import {
  Drawer,
  Toolbar,
  Box,
  Divider,
  Slide
} from '@mui/material'

import TemplatesList from './TemplatesList'
import TemplateDataList from './TemplateDataList'
import EnvironsList from './EnvironsList'
import useProject from '../api/useProject'

const drawerWidth = 240

const AppDrawer = () => {
  const mainMenu = useProject(state => state.mainMenu)
  const dataType = useProject(state => state.dataType)

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
      <Toolbar />
      <Slide direction='down' in={mainMenu} mountOnEnter unmountOnExit>
        <Box sx={{ overflow: 'auto' }}>
          <TemplatesList />
          <Divider />
          <EnvironsList />
        </Box>
      </Slide>
      <Slide direction='up' in={!mainMenu} mountOnEnter unmountOnExit>
        <Box sx={{ overflow: 'auto' }}>
          {
            dataType === 'template' &&
            <TemplateDataList />
          }
        </Box>
      </Slide>
    </Drawer>
  )
}

export default AppDrawer
