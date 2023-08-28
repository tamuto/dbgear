import { useNavigate } from 'react-router-dom'
import {
  useForm
} from 'react-hook-form'
import { useTranslation } from 'react-i18next'
import { enqueueSnackbar } from 'notistack'

import useAxios from '~/api/useAxios'
import useProject from '~/api/useProject'

const useEnvironSettings = () => {
  const axios = useAxios()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const updateEnvirons = useProject(state => state.updateEnvirons)
  const { control, handleSubmit } = useForm({
    defaultValues: {
      id: '',
      name: '',
      base: '',
      description: '',
      instance: '',
      deployment: false
    }
  })

  const onSubmit = handleSubmit((data) => {
    const mapData: NewMapping = {
      base: data.base,
      name: data.name,
      instances: [data.instance],
      description: data.description,
      deployment: data.deployment
    }
    axios<null>(`/environs/${data.id}`).post(mapData, () => {
      enqueueSnackbar(t('message.saveSuccess'), { variant: 'success' })
      updateEnvirons()
      navigate('/')
    })
  })

  return {
    control,
    onSubmit,
  }
}

export default useEnvironSettings
