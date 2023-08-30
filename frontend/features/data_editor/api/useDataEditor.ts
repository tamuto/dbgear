import { useMemo, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
  useGridApiRef
} from '@mui/x-data-grid'

import useVisibility from './useVisibility'
import useManipulate from './useManipulate'

const useDataEditor = () => {
  const { data } = useOutletContext<{data: Data}>()
  const apiRef = useGridApiRef()

  const visibility = useVisibility()
  const manipulate = useManipulate(apiRef)

  const columns = useMemo(() => {
    if (data.info.gridColumns) {
      return data.info.gridColumns.map(({type, items, hide, ...props}) => (
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
    const model: { [key: string]: boolean } = {}
    if (data.info.gridColumns) {
      for (const item of data.info.gridColumns.filter(x => x.hide)) {
        model[item.field] = false
      }
    }
    return model
  }, [data])
  const rows = useMemo(() => {
    return data.info.gridRows
  }, [data])

  useEffect(() => {
    apiRef.current.setColumnVisibilityModel(visibility.allColumns ? {} : columnVisibilityModel)
  }, [visibility.allColumns, columnVisibilityModel])

  return {
    apiRef,
    columns,
    rows,
    initialState: {
      columns: {
        columnVisibilityModel
      }
    },
    features: {
      disabledAppendAndRemove: !data.info.allowLineAdditionAndRemoval,
      visibility,
      manipulate
    },
  }
}

export default useDataEditor
