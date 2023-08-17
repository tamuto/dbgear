import { useMemo } from 'react'
import { Link, useParams, useLocation } from 'react-router-dom'
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
  const dataList = useProject(state => state.dataList)
  const mapping = useProject(state => state.currentMapping)
  const { pathname } = useLocation()
  const { id } = useParams()

  const postfix = useMemo(() => {
    const sp = pathname.split('/')
    if (sp.length > 4) {
      return sp[sp.length - 1]
    }
    return '_data'
  }, [pathname])

  return (
    <List component='nav' subheader={
      <ListSubheader component={Link} to={`/environs/${id}`}>{mapping?.name}</ListSubheader>
    }>
      <ListItemButton component={Link} to={`/environs/${id}/_init`}>
        <ListItemIcon>
          <PlaylistAddCircleIcon />
        </ListItemIcon>
        <ListItemText>Add Data</ListItemText>
      </ListItemButton>
      {
        dataList.map(item => (
          <ListItemButton
            key={item.tableName}
            component={Link}
            to={`/environs/${id}/${item.instance}/${item.tableName}/${postfix}`}
          >
            <ListItemText
              primary={`${item.instance}.${item.tableName}`}
              secondary={item.displayName} />
          </ListItemButton>
        ))
      }
    </List>
  )
}

export default DataList
