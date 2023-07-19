import { useState, useEffect } from 'react'
import { useNavigate, useParams, useOutletContext } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import axios from 'axios'

import useProject from '~/api/useProject'
import useFieldMgr from '~/api/useFieldMgr'

const useTemplateDataSettings = () => {
  const data = useOutletContext()
  const updateDataList = useProject(state => state.updateDataList)
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
    if (!data) {
      _init()
    }
  }, [])

  useEffect(() => {
    if (data) {
      setValue('table', `${data.instance}.${data.info.tableName}`)
    }
  }, [data])

  useEffect(() => {
    fieldMgr.retrieveTableInfo(table, data?.settings)
  }, [table])

  const onSubmit = handleSubmit(async (values) => {
    const [instance, tableName] = values.table.split('.')
    const settings = fieldMgr.filterForSave(values)
    if (data) {
      // TODO update
    } else {
      const result = await axios.post(`/templates/${id}`, {
        instance,
        tableName,
        layout: values.layout,
        settings
      })
      if (result.data.status === 'OK') {
        await updateDataList('template', id)
        navigate(`/templates/${id}/${instance}/${tableName}/_data`)
      }
    }
  })

  return {
    control,
    onSubmit,
    layout,
    tableList,
    fields: fieldMgr.fields,
    columnSettings: fieldMgr.columnSettings,
    editMode: data !== undefined
  }
}

export default useTemplateDataSettings
