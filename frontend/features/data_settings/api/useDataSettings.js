import { useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import axios from 'axios'

const useDataSettings = () => {
  const { id } = useParams()
  const { control, handleSubmit, watch } = useForm({
    defaultValues: {
      table: 'test',
      layout: 'table'
    }
  })
  const { layout } = watch()

  const _init = async () => {
    const result = await axios.get(`/templates/${id}/init`)
    console.log(result.data)
  }

  useEffect(() => {
    _init()
  }, [])

  const onSubmit = handleSubmit(async (data) => {
    console.log(data)
    // const result = await axios.post(`/templates/${id}/${data.table}/${data.layout}`)

  })

  return {
    control,
    onSubmit,
    layout
  }
}

export default useDataSettings
