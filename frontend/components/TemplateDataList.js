import { useEffect, useMemo } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import {
  List,
  ListSubheader,
  ListItemButton,
  ListItemIcon,
  ListItemText
} from '@mui/material'

import PlaylistAddCircleIcon from '@mui/icons-material/PlaylistAddCircle'

import useProject from '~/api/useProject'

const TemplateDataList = () => {
  const subMenuTitle = useProject(state => state.subMenuTitle)
  const subBasePath = useProject(state => state.subBasePath)
  const updateDataList = useProject(state => state.updateDataList)
  const templateDataList = useProject(state => state.templateDataList)
  const { id } = useParams()
  const location = useLocation()

  const postfix = useMemo(() => {
    const sp = location.pathname.split('/')
    if (sp.length > 4) {
      return sp[sp.length - 1]
    }
    return '_data'
  }, [location.pathname])

  useEffect(() => {
    updateDataList('template', id)
  }, [subBasePath])

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
      {
        templateDataList.map(item => (
          <ListItemButton
            key={item.tableName}
            component={Link}
            to={`${subBasePath}/${item.instance}/${item.tableName}/${postfix}`}
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

export default TemplateDataList
