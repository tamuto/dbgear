import { css } from '@emotion/react'
import { Link } from 'react-router-dom'
import {
  Drawer,
  Box,
  Divider,
  Slide,
  Typography
} from '@mui/material'

import imgDBGear from '~/resources/img/dbgear.png'

import TemplatesList from './TemplatesList'
import TemplateDataList from './TemplateDataList'
import EnvironsList from './EnvironsList'
import useProject from '../api/useProject'

const drawerWidth = 240

const logo = css`
  display: flex;
  align-items: center;
  background-color: #86ccce;
  margin-top: 16px;
  margin-left: 5px;
  margin-right: 5px;
  padding-left: 15px;
  padding-top: 5px;
  padding-bottom: 5px;
  border: solid 1px grey;
  border-radius: 20px;
  text-decoration: none;
  color: rgba(0,0,0,0.87);
  font-weight: bold;

  &:visited {
    color: rgba(0,0,0,0.87);
  }
`

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
      <Typography variant='h6' component={Link} to='/' css={logo}>
        <img src={imgDBGear} width='32px' style={{ marginRight: '15px'}} />
        DB Gear
      </Typography>
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
