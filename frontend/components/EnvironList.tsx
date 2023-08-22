import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
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

  return (
    <List component='nav' subheader={
      <ListSubheader>{t('caption.environs')}</ListSubheader>
    }>
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
