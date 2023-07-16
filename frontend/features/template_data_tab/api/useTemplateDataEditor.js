import { useMemo } from 'react'
import {
  useGridApiRef
} from '@mui/x-data-grid'

const useTemplateDataEditor = (data) => {
  const apiRef = useGridApiRef()

  // const rows = [
  //   {id: 1, col1: 'Test1', col2: 'TestA' },
  //   {id: 2, col1: 'Test2', col2: 'TestB' },
  //   {id: 3, col1: 'Test3', col2: 'TestC' },
  // ]

  // const columns = [
  //   { field: 'col1', headerName: 'Column1', width: 150, editable: true },
  //   { field: 'col2', headerName: 'Column2', width: 100 }
  // ]

  const columns = useMemo(() => {
    return data.info.fields.map(item => (
      {
        field: item.columnName,
        headerName: item.displayName,
        editable: true
      }
    ))
  }, [data])
  const rows = []

  return {
    apiRef,
    columns,
    rows
  }
}

export default useTemplateDataEditor
