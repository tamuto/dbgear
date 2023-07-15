import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import axios from 'axios'

const useDataSettings = () => {
  const { id } = useParams()
  const { control, handleSubmit, watch } = useForm({
    defaultValues: {
      table: '',
      layout: 'table'
    }
  })
  const { layout } = watch()
  const [tableList, setTableList] = useState([])

  const _init = async () => {
    const result = await axios.get(`/templates/${id}/init`)
    setTableList(result.data)
  }

  useEffect(() => {
    _init()
  }, [])

  const onSubmit = handleSubmit(async (data) => {
    const [instance, tableName] = data.table.split('.')
    console.log(data)
    const result = await axios.post(`/templates/${id}`, {
      instance,
      tableName,
      layout: data.layout
    })
    console.log(result.data)
  })

  return {
    control,
    onSubmit,
    layout,
    tableList
  }
}

export default useDataSettings
