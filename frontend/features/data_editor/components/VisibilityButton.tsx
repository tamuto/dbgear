import { FC } from 'react'
import {
  ToggleButton,
} from '@mui/material'

import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'

type VisibilityButtonProps = {
  visibility: {
    allColumns: boolean,
    triggerColumns: () => void
  }
}

const VisibilityButton: FC<VisibilityButtonProps> = ({ visibility }) => {
  const { allColumns, triggerColumns } = visibility

  return (
    <ToggleButton
      value='visibility'
      selected={allColumns}
      onClick={triggerColumns}
      size='small'
    >
      {
        allColumns ?
        <VisibilityIcon fontSize='small' /> :
        <VisibilityOffIcon fontSize='small' />
      }
    </ToggleButton>
  )
}

export default VisibilityButton
