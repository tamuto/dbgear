import { useTranslation } from 'react-i18next'
import {
  Button,
  ButtonGroup,
  Stack,
  ToggleButton
} from '@mui/material'
import {
  DataGrid
} from '@mui/x-data-grid'

import CheckIcon from '@mui/icons-material/Check'
import DownloadIcon from '@mui/icons-material/Download';
import PlaylistAddIcon from '@mui/icons-material/PlaylistAdd'
import PlaylistRemoveIcon from '@mui/icons-material/PlaylistRemove'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import UploadIcon from '@mui/icons-material/Upload'

import useDataEditor from '../api/useDataEditor'

const TemplateDataEditor = () => {
  const { t } = useTranslation()
  const {
    apiRef,
    columns,
    rows,
    initialState,
    allColumns,
    triggerColumns,
    append,
    remove,
    save,
    disabledAppendAndRemove
  } = useDataEditor()

  return (
    <Stack sx={{ height: 'calc(100vh - 150px)' }}>
      <Stack direction='row'>
        <Button
          size='small'
          color='success'
          startIcon={<CheckIcon />}
          onClick={save}
        >
          {t('caption.save')}
        </Button>
        <Button size='small' variant='outlined' startIcon={<DownloadIcon />}>
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
        <Button
          size='small'
          color='secondary'
          startIcon={<UploadIcon />}
          sx={{ ml: 3 }}
        >
          {t('caption.upload')}
        </Button>
      </Stack>
      <DataGrid
        apiRef={apiRef}
        rows={rows}
        columns={columns}
        initialState={initialState}
        autoPageSize
      />
    </Stack>
  )
}

export default TemplateDataEditor
