import { css } from '@emotion/react'
import { Link } from 'react-router-dom'
import {
  Drawer,
  Box,
  Slide,
  Typography
} from '@mui/material'

import EnvironList from '~/cmp/EnvironList'
import DataList from '~/cmp/DataList'
import useProject from '~/api/useProject'

import imgDBGear from '~/img/dbgear.png'

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
          <EnvironList />
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
