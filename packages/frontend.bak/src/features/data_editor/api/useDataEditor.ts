import { useMemo, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
  useGridApiRef
} from '@mui/x-data-grid'

import useVisibility from './useVisibility'
import useManipulate from './useManipulate'

type ValueCaption = {
  value: string
  caption: string
}

const useDataEditor = () => {
  const { data, reload } = useOutletContext<{data: Data, reload: (segment: string | null) => void}>()
  const apiRef = useGridApiRef()

  const visibility = useVisibility()

  const columns = useMemo(() => {
    if (data.info.gridColumns) {
      return data.info.gridColumns.map(({type, items, hide, ...props}) => (
        {
          ...props,
          type,
          valueOptions: items,
          getOptionValue: (option: ValueCaption) => option.value,
          getOptionLabel: (option: ValueCaption) => option.caption,
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
  const segment = useMemo(() => {
    return data.info.current
  }, [data])
  const manipulate = useManipulate(apiRef, segment)

  useEffect(() => {
    apiRef.current.setColumnVisibilityModel(visibility.allColumns ? {} : columnVisibilityModel)
  }, [apiRef, visibility.allColumns, columnVisibilityModel])

  const onChangeSegment = (segment: string) => {
    reload(segment)
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
    features: {
      segments: data.info.segments,
      segment,
      onChangeSegment,
      disabledAppendAndRemove: !data.info.allowLineAdditionAndRemoval,
      visibility,
      manipulate,
      columns: data.info.gridColumns,
      rowCount: data.info.gridRows.length,
    },
  }
}

export default useDataEditor
