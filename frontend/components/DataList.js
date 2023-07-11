import { Link } from 'react-router-dom'
import {
  List,
  ListSubheader,
  ListItemButton,
  ListItemIcon,
  ListItemText
} from '@mui/material'

import PlaylistAddCircleIcon from '@mui/icons-material/PlaylistAddCircle'

import useProject from '~/api/useProject'

const DataList = () => {
  const subMenuTitle = useProject(state => state.subMenuTitle)
  const subBasePath = useProject(state => state.subBasePath)
  return (
    <List component='nav' subheader={
      <ListSubheader>{subMenuTitle}</ListSubheader>
    }>
      <ListItemButton component={Link} to={`${subBasePath}/_init`}>
        <ListItemIcon>
          <PlaylistAddCircleIcon />
        </ListItemIcon>
        <ListItemText>Add Data</ListItemText>
      </ListItemButton>
    </List>
  )
}

export default DataList
