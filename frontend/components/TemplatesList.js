import { Link } from 'react-router-dom'
import {
  List,
  ListSubheader,
  ListItemButton,
  ListItemIcon,
  ListItemText
} from '@mui/material'

import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder'

import useProject from '~/api/useProject'

const TemplatesList = () => {
  const projectInfo = useProject(state => state.projectInfo)

  return (
    <List component='nav' subheader={
      <ListSubheader>Templates</ListSubheader>
    }>
      <ListItemButton component={Link} to='/add_template'>
        <ListItemIcon>
          <CreateNewFolderIcon />
        </ListItemIcon>
        <ListItemText>Add Template</ListItemText>
      </ListItemButton>
      {
        projectInfo?.templates.map(item => (
          <ListItemButton key={item.id} component={Link} to={`/templates/${item.id}`}>
            <ListItemText>{item.name}</ListItemText>
          </ListItemButton>
        ))
      }
    </List>
  )
}

export default TemplatesList
