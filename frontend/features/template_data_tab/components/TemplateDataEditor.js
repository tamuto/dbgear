import {
  Button,
  ButtonGroup,
  Stack
} from '@mui/material'

import {
  DataGrid
} from '@mui/x-data-grid'

import useTemplateDataEditor from '../api/useTemplateDataEditor'

const TemplateDataEditor = () => {
  const {
    apiRef,
    columns,
    rows,
    append,
    lotofappend
  } = useTemplateDataEditor()

  return (
    <Stack sx={{ height: 'calc(100vh - 150px)' }}>
      <ButtonGroup>
        <Button onClick={() => append()}>ADD</Button>
        <Button onClick={() => lotofappend()}>LOTS</Button>
      </ButtonGroup>
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
