import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'

import useProject from '~/api/useProject'
import useColumnSettings from './useColumnSettings'
import useFieldItems from './useFieldItems'
import nxio from '~/api/nxio'

import { FK } from './const'

const useDataSettings = (data: Data | null, reload: (() => void) | null) => {
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
      segment: '',
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
    columnFields,
  } = useColumnSettings(setValue, unregister)
  const {
    fieldItems
  } = useFieldItems()

  useEffect(() => {
    nxio<DataFilename[]>(`/environs/${id}/init`).get(result => {
      setTableList(result)
    })
  }, [id])

  useEffect(() => {
    if (data) {
      setValue('table', `${data.model.instance}.${data.model.tableName}`)
      setValue('description', data.model.description)
      setValue('syncMode', data.model.syncMode)
      setValue('layout', data.model.layout)
      setValue('value', data.model.value ?? '')
      setValue('caption', data.model.caption ?? '')
      setValue('segment', data.model.segment ?? '')
      setValue('xAxis', data.model.xAxis ?? '')
      setValue('yAxis', data.model.yAxis ?? '')
      setValue('cells', data.model.cells ?? [])
      setupField(data.table, data.model.settings)
    }
  }, [data, setValue, setupField])

  useEffect(() => {
    // 対象テーブルのプルダウン変更時の処理
    if (!data) {
      retrieveTableInfo(table)
    }
  }, [data, retrieveTableInfo, table])

  const onSubmit = handleSubmit(async (values) => {
    const [instance, tableName] = values.table.split('.')
    const newDM: NewDataModel = {
      description: values.description,
      layout: values.layout,
      settings: {},
      syncMode: values.syncMode,
      value: values.value,
      caption: values.caption,
      segment: values.segment,
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
      console.log(val)
      if (val.startsWith(FK)) {
        const [typ, id, ins, tbl] = val.split(/[:\/\.]/)
        console.log(typ, id, ins, tbl)
        newDM.settings[key] = {
          type: typ,
          id: id,
          instance: ins,
          table: tbl,
        }
      } else {
        console.log('not refs')
        newDM.settings[key] = {
          type: val,
        }
      }
      if (!Number.isNaN(width)) {
        newDM.settings[key].width = width
      }
    }
    await nxio<null>(`/environs/${id}/tables/${instance}/${tableName}`).post(newDM, () => {})
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
