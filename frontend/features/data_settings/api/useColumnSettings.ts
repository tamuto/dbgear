import { useState, useCallback } from 'react'
import { UseFormSetValue, UseFormUnregister } from 'react-hook-form'
import useProject from '~/api/useProject'
import nxio from '~/api/nxio'

import { FK } from './const'

const _makeFieldName = (field: Field): string => `fields.${field.columnName}`
const _judgeDefvalue = (
  projectInfo: ProjectInfo,
  field: Field,
  settings: { [key: string]: SettingValue } | undefined
): string => {
  if (settings && field.columnName in settings) {
    if (settings[field.columnName].type === FK) {
      const id = settings[field.columnName].id
      const ins = settings[field.columnName].instance
      const tbl = settings[field.columnName].table
      return `${FK}:${id}/${ins}.${tbl}`
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

const _judgeWidth = (field: Field, settings: { [key: string]: SettingValue } | undefined): string => {
  if (settings && field.columnName in settings) {
    return settings[field.columnName].width?.toString() || ''
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
      defValue: _judgeDefvalue(projectInfo, field, settings),
      width: _judgeWidth(field, settings)
    })
  }
  return ret
}

const useColumnSettings = (setValue: UseFormSetValue<FormValues>, unregister: UseFormUnregister<FormValues>) => {
  const projectInfo = useProject(state => state.projectInfo)
  const [columnFields, setColumnFields] = useState<ColumnSettings[]>([])

  const _resetFields = useCallback((newFields: ColumnSettings[]) => {
    for (const field of columnFields) {
      if (field.name.startsWith('fields.')) {
        unregister(`fields.${field.key}`)
        unregister(`fields.${field.key}_width`)
      }
    }
    for (const field of newFields) {
      setValue(`fields.${field.key}`, field.defValue)
      setValue(`fields.${field.key}_width`, field.width)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const retrieveTableInfo = useCallback(async (table: string) => {
    if (table === '') {
      return
    }
    const [instance, tableName] = table.split('.')
    nxio<Table>(`/tables/${instance}/${tableName}`).get(result => {
      const newFields = _buildField(projectInfo!, result)
      _resetFields(newFields)
      setColumnFields(newFields)
    })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const setupField = useCallback((table: Table, settings: { [key: string]: SettingValue }) => {
    const newFields = _buildField(projectInfo!, table, settings)
    _resetFields(newFields)
    setColumnFields(newFields)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return {
    retrieveTableInfo,
    setupField,
    columnFields
  }
}

export default useColumnSettings
