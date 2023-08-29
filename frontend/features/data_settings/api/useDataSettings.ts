import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'

import useProject from '~/api/useProject'
import useColumnSettings from './useColumnSettings'
import useAxios from '~/api/useAxios'

import { FK } from './const'

type FormValues = {
  table: string
  description: string
  syncMode: string
  value: string
  caption: string
  layout: string
  xAxis: string
  yAxis: string
  cells: string
  fields: { [key: string]: string }
}

const useDataSettings = (data: Data | null) => {
  const axios = useAxios()
  const navigate = useNavigate()
  const updateDataList = useProject(state => state.updateDataList)
  const { id } = useParams()
  // TODO: cellsは複数にする
  const { control, handleSubmit, watch, setValue, unregister } = useForm<FormValues>({
    defaultValues: {
      table: '',
      description: '',
      syncMode: '',
      value: '',
      caption: '',
      layout: '',
      xAxis: '',
      yAxis: '',
      cells: '',
      fields: {}
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
    const [instance, tableName] = values.table.split('.')
    const data: NewDataModel = {
      description: values.description,
      layout: values.layout,
      settings: {},
      syncMode: values.syncMode,
      value: values.value,
      caption: values.caption,
      xAxis: values.xAxis,
      yAxis: values.yAxis,
      cells: [values.cells]
    }
    for (const key of Object.keys(values.fields)) {
      const val: string = values.fields[key]
      if (val === '') {
        continue
      }
      if (val.startsWith(FK)) {
        const fkTable = val.split('.')[1]
        data.settings[key] = {
          type: FK,
          value: fkTable
        }
      } else {
        data.settings[key] = {
          type: val,
        }
      }
    }
    console.log(data)
    await axios<null>(`/environs/${id}/tables/${instance}/${tableName}`).post(data, () => {})
    await updateDataList(id)
    navigate(`/environs/${id}/${instance}/${tableName}/_data`)
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
