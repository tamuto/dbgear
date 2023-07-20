import {
  Button,
  ButtonGroup,
  FormControlLabel,
  Stack,
  Switch,
  ToggleButton
} from '@mui/material'

import {
  DataGrid
} from '@mui/x-data-grid'

import useTemplateDataEditor from '../api/useTemplateDataEditor'

import CheckIcon from '@mui/icons-material/Check'
import DownloadIcon from '@mui/icons-material/Download';
import PlaylistAddIcon from '@mui/icons-material/PlaylistAdd'
import PlaylistRemoveIcon from '@mui/icons-material/PlaylistRemove'
import VisibilityIcon from '@mui/icons-material/Visibility'
import VisibilityOffIcon from '@mui/icons-material/VisibilityOff'
import UploadIcon from '@mui/icons-material/Upload'

const TemplateDataEditor = () => {
  const {
    apiRef,
    columns,
    rows,
    initialState,
    allColumns,
    triggerColumns,
    append,
    remove,
    save
  } = useTemplateDataEditor()

  return (
    <Stack sx={{ height: 'calc(100vh - 150px)' }}>
      <Stack direction='row'>
        <Button
          size='small'
          variant='outlined'
          color='success'
          startIcon={<CheckIcon />}
          onClick={save}
        >
          Save
        </Button>
        <Button size='small' variant='outlined' startIcon={<DownloadIcon />}>
          Download
        </Button>
        <ButtonGroup>
          <Button onClick={append} startIcon={<PlaylistAddIcon />}>
            Append
          </Button>
          <Button onClick={remove} startIcon={<PlaylistRemoveIcon />}>
            Remove
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
          variant='outlined'
          color='secondary'
          startIcon={<UploadIcon />}
          sx={{ ml: 3 }}
        >
          Upload
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
