import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import axios from 'axios'

import useProject from '~/api/useProject'
import useFieldMgr from '~/api/useFieldMgr'

const useTemplateDataSettings = () => {
  const updateDataList = useProject(state => state.updateDataList)
  const subBasePath = useProject(state => state.subBasePath)
  const { id } = useParams()
  const navigate = useNavigate()
  const { control, handleSubmit, watch, setValue, unregister } = useForm({
    defaultValues: {
      table: '',
      layout: 'table'
    }
  })
  const { table, layout } = watch()
  const [tableList, setTableList] = useState([])
  const fieldMgr = useFieldMgr(setValue, unregister)

  const _init = async () => {
    const result = await axios.get(`/templates/${id}/init`)
    setTableList(result.data)
  }

  useEffect(() => {
    _init()
  }, [])

  useEffect(() => {
    fieldMgr.retrieve_table_info(table)
  }, [table])

  const onSubmit = handleSubmit(async (data) => {
    console.log(data)
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
    tableList,
    fields: fieldMgr.fields,
    columnSettings: fieldMgr.columnSettings
  }
}

export default useTemplateDataSettings
