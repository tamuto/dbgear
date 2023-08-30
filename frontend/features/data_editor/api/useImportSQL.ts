import { useState } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import {
  useForm
} from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { enqueueSnackbar } from 'notistack'
import useAxios from '~/api/useAxios'

const useImportSQL = () => {
  const { t } = useTranslation()
  const axios = useAxios()
  const { reload } = useOutletContext<{reload: () => void}>()
  const { id, instance, table } = useParams()
  const [open, setOpen] = useState(false)

  const { control, handleSubmit } = useForm({
    defaultValues: {
      host: 'localhost',
      sql: ''
    }
  })

  const onSubmit = handleSubmit(async (data) => {
    await axios<null>(`/environs/${id}/tables/${instance}/${table}/import`).post(data, () => {
      enqueueSnackbar(t('message.importSuccess'), { variant: 'success' })
      reload()
    })
    setOpen(false)
  })

  return {
    setOpen,
    open,
    control,
    onSubmit
  }
}

export default useImportSQL
