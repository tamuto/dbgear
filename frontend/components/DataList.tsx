import { useState, useEffect, useMemo } from 'react'
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
import useAxios from '~/api/useAxios'

const DataList = () => {
  const [dataList, setDataList] = useState<DataFilename[]>([])

  const subMenuTitle = useProject(state => state.subMenuTitle)
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
    if (id) {
      useAxios<DataFilename[]>(`/environs/${id}/tables`).get((result) => {
        console.log(result)
        setDataList(result)
      })
    }
  }, [id])

  return (
    <List component='nav' subheader={
      <ListSubheader>{subMenuTitle}</ListSubheader>
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
