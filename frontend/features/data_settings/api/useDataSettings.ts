import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'

// import useProject from '~/api/useProject'
import useColumnSettings from './useColumnSettings'
import useAxios from '~/api/useAxios'

const useDataSettings = (data: Data | null) => {
  // const navigate = useNavigate()
  // const updateDataList = useProject(state => state.updateDataList)
  const { id } = useParams()
  const { control, handleSubmit, watch, setValue, unregister } = useForm({
    defaultValues: {
      table: '',
      description: '',
      syncMode: '',
      value: '',
      caption: '',
      layout: 'table',
      x_axis: '',
      y_axis: '',
      cells: '',
    }
  })
  const { table, layout } = watch()
  const [tableList, setTableList] = useState<DataFilename[]>([])
  const {
    retrieveTableInfo,
    columnFields,
    fieldItems
  } = useColumnSettings(setValue, unregister)

  useEffect(() => {
    useAxios<DataFilename[]>(`/environs/${id}/init`).get(result => {
      setTableList(result)
    })
  }, [])

  useEffect(() => {
    // if (data) {
    //   setValue('table', `${data.instance}.${data.info.tableName}`)
    //   setValue('description', data.description)
    //   setValue('layout', data.layout)
    // }
  }, [data])

  useEffect(() => {
    retrieveTableInfo(table, data?.model.settings)
  }, [table])

  const onSubmit = handleSubmit(async (values) => {
    // const [instance, tableName] = values.table.split('.')
    // const settings = fieldMgr.filterForSave(values)
    // if (data) {
    //   const result = await axios.put(`/templates/${id}`, {
    //     instance,
    //     tableName,
    //     description: values.description,
    //     layout: values.layout,
    //     settings
    //   })
    //   if (result.data.status === 'OK') {
    //     // await initData()
    //   }
    // } else {
    //   const result = await axios.post(`/templates/${id}`, {
    //     instance,
    //     tableName,
    //     description: values.description,
    //     layout: values.layout,
    //     settings
    //   })
    //   if (result.data.status === 'OK') {
    //     // await updateDataList('template', id)
    //     // navigate(`/templates/${id}/${instance}/${tableName}/_data`)
    //   }
    // }
  })

  return {
    control,
    onSubmit,
    layout,
    tableList,
    columnFields,
    fieldItems,
    editMode: data !== null
  }
}

export default useDataSettings
