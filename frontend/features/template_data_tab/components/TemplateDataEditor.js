import {
  Stack
} from '@mui/material'

import {
  DataGrid
} from '@mui/x-data-grid'

import useTemplateDataEditor from '../api/useTemplateDataEditor'

const TemplateDataEditor = ({ data }) => {
  const {
    apiRef,
    columns,
    rows
  } = useTemplateDataEditor(data)

  return (
    <Stack>
      <DataGrid apiRef={apiRef} rows={rows} columns={columns} sx={{ height: '100px' }} />
    </Stack>
  )
}

export default TemplateDataEditor
