import { useState } from 'react'
import { useOutletContext, useParams } from 'react-router-dom'
import {
  useForm
} from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { enqueueSnackbar } from 'notistack'
import nxio from '~/api/nxio'

const useImportSQL = (segment: string | null) => {
  const { t } = useTranslation()
  const { reload } = useOutletContext<{reload: (segment: string | null) => void}>()
  const { id, instance, table } = useParams()
  const [open, setOpen] = useState(false)

  const { control, handleSubmit } = useForm({
    defaultValues: {
      host: 'localhost',
      sql: ''
    }
  })

  const onSubmit = handleSubmit(async (data) => {
    await nxio<null>(`/environs/${id}/tables/${instance}/${table}/import`, { segment }).post(data, () => {
      enqueueSnackbar(t('message.importSuccess'), { variant: 'success' })
      reload(segment)
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
