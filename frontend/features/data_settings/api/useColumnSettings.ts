import { useState } from 'react'
import useProject from '~/api/useProject'
import useAxios from '~/api/useAxios'

import { FK } from './const'

const _makeFieldName = (field: Field): string => `fields.${field.columnName}`
const _judgeDefvalue = (
  projectInfo: ProjectInfo,
  field: Field,
  settings: { [key: string]: SettingValue } | undefined
): string | object => {
  if (settings && field.columnName in settings) {
    if (settings[field.columnName].type === FK) {
      return `${FK}.${settings[field.columnName].value}`
    }
    return settings[field.columnName].type
  }
  for (const [rule, value] of Object.entries(projectInfo.rules)) {
    const re = new RegExp(rule)
    if (re.test(field.columnName)) {
      return value
    }
  }
  return ''
}

const _buildField = (
  projectInfo: ProjectInfo,
  tableInfo: Table,
  settings: { [key: string]: SettingValue } | undefined = undefined
): ColumnSettings[] => {
  const ret: ColumnSettings[] = []
  for (const field of tableInfo.fields) {
    ret.push({
      key: field.columnName,
      label: field.displayName,
      name: _makeFieldName(field),
      defvalue: _judgeDefvalue(projectInfo, field, settings)
    })
  }
  return ret
}

const useColumnSettings = (setValue: Function, unregister: Function) => {
  const axios = useAxios()
  const projectInfo = useProject(state => state.projectInfo)
  const dataList = useProject(state => state.dataList)
  const [columnFields, setColumnFields] = useState<ColumnSettings[]>([])
  const [fieldItems, setFieldItems] = useState<FieldItem[]>([])

  const _resetFields = (newFields: ColumnSettings[]) => {
    for (const field of columnFields) {
      unregister(field.name)
    }
    for (const field of newFields) {
      setValue(field.name, field.defvalue)
    }
  }

  const retrieveTableInfo = async (table: string) => {
    if (table === '') {
      return
    }
    const [instance, tableName] = table.split('.')
    axios<Table>(`/tables/${instance}/${tableName}`).get(result => {
      const newFields = _buildField(projectInfo!, result)
      _resetFields(newFields)
      setColumnFields(newFields)
    })
  }

  const setupField = (table: Table, settings: { [key: string]: SettingValue }) => {
    const newFields = _buildField(projectInfo!, table, settings)
    _resetFields(newFields)
    setColumnFields(newFields)
  }

  const setupFieldItems = () => {
    const data = [
      ...Object.keys(projectInfo!.bindings).map(key => {
        const item: FieldItem = {
          value: key,
          caption: projectInfo!.bindings[key].value,
        }
        return item
      }),
      ...dataList.map(data => {
        const item: FieldItem = {
          value: `${FK}:${data.instance}.${data.tableName}`,
          caption: `${data.instance}.${data.tableName} (${data.displayName})`,
        }
        return item
      }).sort((a, b) => { return a.caption.localeCompare(b.caption) })
    ]
    setFieldItems(data)
  }

  return {
    retrieveTableInfo,
    setupField,
    setupFieldItems,
    columnFields,
    fieldItems
  }
}

export default useColumnSettings
