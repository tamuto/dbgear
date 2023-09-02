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
  cells: string[]
  fields: { [key: string]: string }
}

const useDataSettings = (data: Data | null, reload: (() => void) | null) => {
  const axios = useAxios()
  const navigate = useNavigate()
  const updateDataList = useProject(state => state.updateDataList)
  const { id } = useParams()
  const { control, handleSubmit, watch, setValue, unregister } = useForm<FormValues>({
    defaultValues: {
      table: '',
      description: '',
      syncMode: '',
      value: '',
      caption: '',
      layout: 'table',
      xAxis: '',
      yAxis: '',
      cells: [],
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
      setValue('cells', data.model.cells ?? [])
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
    const newDM: NewDataModel = {
      description: values.description,
      layout: values.layout,
      settings: {},
      syncMode: values.syncMode,
      value: values.value,
      caption: values.caption,
      xAxis: values.xAxis,
      yAxis: values.yAxis,
      cells: values.cells
    }
    for (const key of Object.keys(values.fields)) {
      if (key.endsWith('_width')) {
        // _widthは無視
        continue
      }
      const val: string = values.fields[key]
      const width: number = parseInt(values.fields[key + '_width'])
      if (val === '' && Number.isNaN(width)) {
        continue
      }
      if (val.startsWith(FK)) {
        const fkTable = val.split(':')[1]
        newDM.settings[key] = {
          type: FK,
          value: fkTable,
        }
      } else {
        newDM.settings[key] = {
          type: val,
        }
      }
      if (!Number.isNaN(width)) {
        newDM.settings[key].width = width
      }
    }
    await axios<null>(`/environs/${id}/tables/${instance}/${tableName}`).post(newDM, () => {})
    if (data) {
      // dataがある場合は、reloadも渡される。
      await reload!()
    } else {
      await updateDataList(id)
      navigate(`/environs/${id}/${instance}/${tableName}/_data`)
    }
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
