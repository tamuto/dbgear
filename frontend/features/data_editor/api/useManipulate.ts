import { MutableRefObject } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { enqueueSnackbar } from 'notistack'
import {
  GridApiCommon
} from '@mui/x-data-grid'

import useAxios from '~/api/useAxios'

const useManipulate = (apiRef: MutableRefObject<GridApiCommon>) => {
  const axios = useAxios()
  const { t } = useTranslation()
  const { id, instance, table } = useParams()

  const append = async () => {
    axios<{ [key: string]: any }>(`/environs/${id}/tables/${instance}/${table}/row`).get(result => {
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
    axios<null>(`/environs/${id}/tables/${instance}/${table}`).put(data, () => {
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
