import { useMemo, useState, useEffect } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  useGridApiRef
} from '@mui/x-data-grid'
import { enqueueSnackbar } from 'notistack'

import useAxios from '~/api/useAxios'

const useDataEditor = () => {
  const { t } = useTranslation()
  const { data } = useOutletContext<{data: Data}>()
  const { id, instance, table } = useParams()
  const apiRef = useGridApiRef()
  const [allColumns, setAllColumns] = useState(false)

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
    apiRef.current.setColumnVisibilityModel(allColumns ? {} : columnVisibilityModel)
  }, [allColumns, columnVisibilityModel])

  const triggerColumns = () => {
    setAllColumns(!allColumns)
  }

  const append = async () => {
    useAxios<{ [key: string]: any }>(`/environs/${id}/tables/${instance}/${table}/row`).get(result => {
      console.log(result)
      apiRef.current.updateRows([result])
    })
  }

  const remove = () => {
    const rows = apiRef.current.getSelectedRows()
    console.log(rows)
    console.log([...rows.values()].map(row => ({ ...row, _action: 'delete' })))
    apiRef.current.updateRows([...rows.values()].map(row => ({ ...row, _action: 'delete' })))
  }

  const save = async () => {
    const data = apiRef.current.getSortedRows()
    useAxios<null>(`/environs/${id}/tables/${instance}/${table}`).put(data, () => {
      enqueueSnackbar(t('message.saveSuccess'), { variant: 'success' })
    })
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
    disabledAppendAndRemove: !data.info.allowLineAdditionAndRemoval
  }
}

export default useDataEditor
