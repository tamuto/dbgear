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
    nxio<null>(`/environs/${id}/tables/${instance}/${table}`, { segment }).put(data, () => {
      enqueueSnackbar(t('message.saveSuccess'), { variant: 'success' })
    })
  }

  return {
    append,
    remove,
    save,
  }
}

export default useManipulate
