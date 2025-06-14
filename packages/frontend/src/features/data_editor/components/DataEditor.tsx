import {
  Stack,
} from '@mui/material'
import {
  DataGrid
} from '@mui/x-data-grid'

import useDataEditor from '../api/useDataEditor'
import FunctionBar from './FunctionBar'

const TemplateDataEditor = () => {
  const {
    apiRef,
    columns,
    rows,
    initialState,
    features
  } = useDataEditor()

  return (
    <>
      <Stack sx={{ height: 'calc(100vh - 150px)' }}>
        <FunctionBar features={features} />
        <DataGrid
          apiRef={apiRef}
          rows={rows}
          columns={columns}
          initialState={initialState}
          autoPageSize
        />
      </Stack>
    </>
  )
}

export default TemplateDataEditor
