import { FC } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Button,
  ButtonGroup,
  Stack,
} from '@mui/material'

import CheckIcon from '@mui/icons-material/Check'
import DownloadIcon from '@mui/icons-material/Download';
import PlaylistAddIcon from '@mui/icons-material/PlaylistAdd'
import PlaylistRemoveIcon from '@mui/icons-material/PlaylistRemove'
import UploadIcon from '@mui/icons-material/Upload'

import VisibilityButton from './VisibilityButton'
import ImportSQLButton from './ImportSQLButton'

type FunctionBarProps = {
  features: {
    disabledAppendAndRemove: boolean,
    visibility: {
      allColumns: boolean,
      triggerColumns: () => void
    }
    manipulate: {
      append: () => void,
      remove: () => void,
      save: () => void
    }
  }
}

const FunctionBar: FC<FunctionBarProps> = ({ features }) => {
  const { t } = useTranslation()
  const { disabledAppendAndRemove, visibility } = features
  const { append, remove, save } = features.manipulate

  return (
    <Stack direction='row'>
      <Button
        size='small'
        color='success'
        startIcon={<CheckIcon />}
        onClick={save}
      >
        {t('caption.save')}
      </Button>
      <Button size='small' variant='outlined' startIcon={<DownloadIcon />} disabled>
        {t('caption.download')}
      </Button>
      <ButtonGroup>
        <Button
          onClick={append}
          startIcon={<PlaylistAddIcon />}
          disabled={disabledAppendAndRemove}
        >
          {t('caption.append')}
        </Button>
        <Button
          onClick={remove}
          startIcon={<PlaylistRemoveIcon />}
          disabled={disabledAppendAndRemove}
        >
          {t('caption.remove')}
        </Button>
      </ButtonGroup>
      <VisibilityButton visibility={visibility} />
      <Button
        size='small'
        color='secondary'
        startIcon={<UploadIcon />}
        disabled
      >
        {t('caption.upload')}
      </Button>
      <ImportSQLButton disabledAppendAndRemove={disabledAppendAndRemove} />
    </Stack>
  )
}

export default FunctionBar