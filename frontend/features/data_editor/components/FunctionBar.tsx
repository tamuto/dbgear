import { FC } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Button,
  ButtonGroup,
  TextField,
  Stack,
  MenuItem
} from '@mui/material'

import CheckIcon from '@mui/icons-material/Check'
import DownloadIcon from '@mui/icons-material/Download';
import PlaylistAddIcon from '@mui/icons-material/PlaylistAdd'
import PlaylistRemoveIcon from '@mui/icons-material/PlaylistRemove'
import UploadIcon from '@mui/icons-material/Upload'

import VisibilityButton from './VisibilityButton'
import ImportSQLButton from './ImportSQLButton'
import FillDataButton from './FillDataButton'

type FunctionBarProps = {
  features: {
    segments: ListItem[] | null,
    segment: string | null,
    onChangeSegment: (segment: string) => void,
    disabledAppendAndRemove: boolean,
    visibility: {
      allColumns: boolean,
      triggerColumns: () => void
    }
    manipulate: {
      append: () => void,
      remove: () => void,
      save: () => void,
      fillData: (method: string, column: string, value: string) => void
    },
    columns: GridColumn[],
    rowCount: number
  }
}

const FunctionBar: FC<FunctionBarProps> = ({ features }) => {
  const { t } = useTranslation()
  const { disabledAppendAndRemove, visibility, segments, columns, rowCount } = features
  const { append, remove, save, fillData } = features.manipulate

  return (
    <Stack direction='row'>
      {
        segments &&
        <TextField
          select
          label={t('caption.segment')}
          value={features.segment}
          onChange={(e) => features.onChangeSegment(e.target.value)}
          sx={{ width: '150px'}}
        >
          {
            segments.map((segment) => (
              <MenuItem key={segment.value} value={segment.value}>
                {segment.caption}
              </MenuItem>
            ))
          }
        </TextField>
      }
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
      <FillDataButton columns={columns} rowCount={rowCount} fillData={fillData} />
      <VisibilityButton visibility={visibility} />
      <Button
        size='small'
        color='secondary'
        startIcon={<UploadIcon />}
        disabled
      >
        {t('caption.upload')}
      </Button>
      <ImportSQLButton disabledAppendAndRemove={disabledAppendAndRemove} segment={features.segment} />
    </Stack>
  )
}

export default FunctionBar
