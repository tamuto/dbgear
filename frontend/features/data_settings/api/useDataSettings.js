import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import axios from 'axios'

import useProject from '~/api/useProject'

const useDataSettings = () => {
  const updateDataList = useProject(state => state.updateDataList)
  const subBasePath = useProject(state => state.subBasePath)
  const { id } = useParams()
  const navigate = useNavigate()
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
    const result = await axios.post(`/templates/${id}`, {
      instance,
      tableName,
      layout: data.layout
    })
    if (result.data.status === 'OK') {
      await updateDataList('template', id)
      navigate(`${subBasePath}/${instance}/${tableName}`)
    }
  })

  return {
    control,
    onSubmit,
    layout,
    tableList
  }
}

export default useDataSettings
