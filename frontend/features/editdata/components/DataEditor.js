import { Button } from '@mui/material'
import { DataGrid, useGridApiRef } from '@mui/x-data-grid'

const rows = [
  {id: 1, col1: 'Test1', col2: 'TestA' },
  {id: 2, col1: 'Test2', col2: 'TestB' },
  {id: 3, col1: 'Test3', col2: 'TestC' },
]

const columns = [
  { field: 'col1', headerName: 'Column1', width: 150, editable: true },
  { field: 'col2', headerName: 'Column2', width: 100 }
]

const DataEditor = () => {
  const apiRef = useGridApiRef()

  const handler = () => {
    console.log(apiRef.current)
    // console.log(apiRef.current.getRowModels())
    console.log(apiRef.current.getSortedRows())
  }

  return (
    <>
      <DataGrid apiRef={apiRef} rows={rows} columns={columns} />
      <Button onClick={handler}>Test</Button>
    </>
  )
}

export default DataEditor
