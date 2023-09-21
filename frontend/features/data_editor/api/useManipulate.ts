import { MutableRefObject } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { enqueueSnackbar } from 'notistack'
import {
  GridApiCommon
} from '@mui/x-data-grid'

import nxio from '~/api/nxio'

const useManipulate = (apiRef: MutableRefObject<GridApiCommon>, segment: string | null) => {
  const { t } = useTranslation()
  const { id, instance, table } = useParams()

  const append = async () => {
    nxio<{ [key: string]: object }>(`/environs/${id}/tables/${instance}/${table}/row`).get(result => {
      apiRef.current.updateRows([result])
      apiRef.current.selectRow(result.id.toString(), true, true)
      apiRef.current.setPage(100)
    })
  }

  const remove = () => {
    const rows = apiRef.current.getSelectedRows()
    apiRef.current.updateRows([...rows.values()].map(row => ({ ...row, _action: 'delete' })))
  }

  const save = async () => {
    const data = apiRef.current.getSortedRows()
    nxio<null>(`/environs/${id}/tables/${instance}/${table}`, {
      params: { segment }
    }).put(data, () => {
      enqueueSnackbar(t('message.saveSuccess'), { variant: 'success' })
    })
  }

  const fillData = (column: string, value: string) => {
    const data = apiRef.current.getSortedRows()
    for (const row of data) {
      row[column] = value
      apiRef.current.updateRows([row])
    }
  }

  return {
    append,
    remove,
    save,
    fillData,
  }
}

export default useManipulate
