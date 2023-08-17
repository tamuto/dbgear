import { Link } from 'react-router-dom'
import {
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText
} from '@mui/material'

import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder'

import useProject from '~/api/useProject'

const EnvironList = () => {
  const environs = useProject(state => state.environs)

  return (
    <List component='nav'>
      <ListItemButton component={Link} to='/add'>
        <ListItemIcon>
          <CreateNewFolderIcon />
        </ListItemIcon>
        <ListItemText>Add Environ</ListItemText>
      </ListItemButton>
      {
        environs.map(item => (
          <ListItemButton key={item.id} component={Link} to={`/environs/${item.id}`}>
            <ListItemText>{item.name}</ListItemText>
          </ListItemButton>
        ))
      }
    </List>
  )
}

export default EnvironList
