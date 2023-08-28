import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'

// import useProject from '~/api/useProject'
import useColumnSettings from './useColumnSettings'
import useAxios from '~/api/useAxios'

const useDataSettings = (data: Data | null) => {
  const axios = useAxios()
  // const navigate = useNavigate()
  // const updateDataList = useProject(state => state.updateDataList)
  const { id } = useParams()
  // TODO: cellsは複数にする
  const { control, handleSubmit, watch, setValue, unregister } = useForm({
    defaultValues: {
      table: '',
      description: '',
      syncMode: '',
      value: '',
      caption: '',
      layout: '',
      xAxis: '',
      yAxis: '',
      cells: ''
      // table: data?.model.tableName ?? '',
      // description: data?.model.description ?? '',
      // syncMode: data?.model.syncMode ?? '',
      // value: data?.model.value ?? '',
      // caption: data?.model.caption ?? '',
      // layout: data?.model.layout ?? '',
      // x_axis: data?.model.xAxis ?? '',
      // y_axis: data?.model.yAxis ?? '' ,
      // cells: data?.model.cells?.[0] ?? ''
    }
  })
  const { table, layout } = watch()
  const [tableList, setTableList] = useState<DataFilename[]>([])
  const {
    retrieveTableInfo,
    setupField,
    setupFieldItems,
    columnFields,
    fieldItems
  } = useColumnSettings(setValue, unregister)

  useEffect(() => {
    setupFieldItems()
    axios<DataFilename[]>(`/environs/${id}/init`).get(result => {
      setTableList(result)
    })
  }, [])

  useEffect(() => {
    if (data) {
      setValue('table', `${data.model.instance}.${data.model.tableName}`)
      setValue('description', data.model.description)
      setValue('syncMode', data.model.syncMode)
      setValue('layout', data.model.layout)
      setValue('value', data.model.value ?? '')
      setValue('caption', data.model.caption ?? '')
      setValue('xAxis', data.model.xAxis ?? '')
      setValue('yAxis', data.model.yAxis ?? '')
      setValue('cells', data.model.cells?.[0] ?? '')
      setupField(data.table, data.model.settings)
    }
  }, [data])

  useEffect(() => {
    // プルダウン変更時の処理
    if (!data) {
      retrieveTableInfo(table)
    }
  }, [table])

  const onSubmit = handleSubmit(async (values) => {
    console.log(values)
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
