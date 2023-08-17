import { useMemo, useState } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import axios from 'axios'
import {
  useGridApiRef
} from '@mui/x-data-grid'

const useTemplateDataEditor = () => {
  const { data } = useOutletContext()
  const { id, instance, tableName } = useParams()
  const apiRef = useGridApiRef()
  const [allColumns, setAllColumns] = useState(false)

  const columns = useMemo(() => {
    if (data.gridColumns) {
      return data.gridColumns.map(({type, items, hide, ...props}) => (
        {
          ...props,
          type,
          valueOptions: items
        }
      ))
    }
    return []
  }, [data])
  const columnVisibilityModel = useMemo(() => {
    const model = {}
    if (data.gridColumns) {
      for (const item of data.gridColumns.filter(x => x.hide)) {
        model[item.field] = false
      }
    }
    return model
  }, [data])
  const rows = useMemo(() => {
    return data.gridRows
  }, [data])

  const triggerColumns = () => {
    apiRef.current.setColumnVisibilityModel(allColumns ? columnVisibilityModel : {})
    setAllColumns(!allColumns)
  }

  const append = async () => {
    const result = await axios.get(`/templates/${id}/${instance}/${tableName}/new_row`)
    console.log(result.data)
    apiRef.current.updateRows([result.data])
  }

  const remove = () => {

  }

  const save = async () => {
    console.log(apiRef.current.getSortedRows())
    await axios.post(`/templates/${id}/${instance}/${tableName}`, apiRef.current.getSortedRows())
  }

  return {
    apiRef,
    columns,
    rows,
    initialState: {
      columns: {
        columnVisibilityModel
      }
    },
    allColumns,
    triggerColumns,
    append,
    remove,
    save,
  }
}

export default useTemplateDataEditor
