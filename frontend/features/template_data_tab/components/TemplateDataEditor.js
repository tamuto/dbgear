import {
  Button,
  ButtonGroup,
  Stack
} from '@mui/material'

import {
  DataGrid
} from '@mui/x-data-grid'

import useTemplateDataEditor from '../api/useTemplateDataEditor'

import CheckIcon from '@mui/icons-material/Check'
import DownloadIcon from '@mui/icons-material/Download';
import PlaylistAddIcon from '@mui/icons-material/PlaylistAdd'
import PlaylistRemoveIcon from '@mui/icons-material/PlaylistRemove'
import UploadIcon from '@mui/icons-material/Upload'

const TemplateDataEditor = () => {
  const {
    apiRef,
    columns,
    rows
  } = useTemplateDataEditor()

  return (
    <Stack sx={{ height: 'calc(100vh - 150px)' }}>
      <Stack direction='row'>
        <Button size='small' variant='outlined' color='success' startIcon={<CheckIcon />}>
          Save
        </Button>
        <Button size='small' variant='outlined' startIcon={<DownloadIcon />}>
          Download
        </Button>
        <ButtonGroup>
          <Button startIcon={<PlaylistAddIcon />}>
            Add
          </Button>
          <Button startIcon={<PlaylistRemoveIcon />}>
            Remove
          </Button>
        </ButtonGroup>
        <div style={{ flexGrow: 1 }}></div>
        <Button size='small' variant='outlined' color='secondary' startIcon={<UploadIcon />}>
          Upload
        </Button>
      </Stack>
      <DataGrid
        apiRef={apiRef}
        rows={rows}
        columns={columns}
        autoPageSize
      />
    </Stack>
  )
}

export default TemplateDataEditor
