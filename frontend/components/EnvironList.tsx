import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Collapse,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  ListSubheader
} from '@mui/material'

import CreateNewFolderIcon from '@mui/icons-material/CreateNewFolder'

import useProject from '~/api/useProject'

const EnvironList = () => {
  const { t } = useTranslation()
  const environs = useProject(state => state.environs)
  const [open, setOpen] = useState('')

  return (
    <List component='nav' subheader={
      <ListSubheader>{t('caption.environs')}</ListSubheader>
    }>
      <ListItemButton component={Link} to='/add'>
        <ListItemIcon>
          <CreateNewFolderIcon />
        </ListItemIcon>
        <ListItemText>{t('caption.addEnviron')}</ListItemText>
      </ListItemButton>
      {
        environs.map(item => (
          <List key={item.name} subheader={
            <ListSubheader
              sx={{ cursor: 'pointer' }}
              onClick={() => setOpen(item.name)}
            >
              {item.name}
            </ListSubheader>}>
            <Collapse in={open===item.name} timeout='auto' unmountOnExit>
              {
                item.children.map(child => (
                  <ListItemButton key={child.id} component={Link} to={`/environs/${child.id}`}>
                    <ListItemText>{child.name}</ListItemText>
                  </ListItemButton>
                ))
              }
            </Collapse>
          </List>
        ))
      }
    </List>
  )
}

export default EnvironList
