import {
  List,
  ListSubheader,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListItem,
  TextField,
  InputAdornment
} from '@mui/material'

import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder'
import SearchIcon from '@mui/icons-material/Search'

import useProject from '../api/useProject'

const EnvironsList = () => {
  const projectInfo = useProject(state => state.projectInfo)

  return (
    <List dense component='nav' subheader={
      <ListSubheader>Environments</ListSubheader>
    }>
      <ListItemButton>
        <ListItemIcon>
          <CreateNewFolderIcon />
        </ListItemIcon>
        <ListItemText>Add Environment</ListItemText>
      </ListItemButton>
      <ListItem>
        <TextField fullWidth size='small' margin='none'
          placeholder='Search...'
          InputProps={{
            startAdornment: (
              <InputAdornment position='start'>
                <SearchIcon />
              </InputAdornment>
            )
          }}
        />
      </ListItem>
      {
        projectInfo?.environs.map(item => (
          <ListItemButton key={item.id}>
            <ListItemText>{item.name}</ListItemText>
          </ListItemButton>
        ))
      }
    </List>
  )
}

export default EnvironsList
