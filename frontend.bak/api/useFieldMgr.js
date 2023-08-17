import { useState } from 'react'
import axios from 'axios'
import useProject from './useProject'

const useFieldMgr = (setValue, unregister) => {
  const FK = 'Foreign Key: '
  const projectInfo = useProject(state => state.projectInfo)
  const [fields, setFields] = useState([])

  const _buildField = (tableInfo, settings) => {
    // TODO settings
    const makeFieldName = (field) => `fields.${field.columnName}`
    const judgeDefvalue = (field) => {
      if (settings && field.columnName in settings) {
        return settings[field.columnName]
      }
      if (field.foreignKey !== null) {
        return `${FK}${field.foreignKey}`
      }
      for (const [rule, value] of Object.entries(projectInfo.rules)) {
        const re = new RegExp(rule)
        if (re.test(field.columnName)) {
          return value
        }
      }
      return ''
    }

    const ret = []
    for (const field of tableInfo.fields) {
      ret.push({
        key: field.columnName,
        type: field.foreignKey === null ? 'select' : 'text',
        label: field.displayName,
        name: makeFieldName(field),
        defvalue: judgeDefvalue(field)
      })
    }
    return ret
  }

  const _resetFields = (newFields) => {
    for (const field of fields) {
      unregister(field.name)
    }
    for (const field of newFields) {
      setValue(field.name, field.defvalue)
    }
  }

  const retrieveTableInfo = async (table, settings) => {
    if (table === '') {
      return
    }
    const [instance, tableName] = table.split('.')
    const result = await axios.get(`/tables/${instance}/${tableName}`)
    const newFields = _buildField(result.data, settings)
    _resetFields(newFields)
    setFields(newFields)
  }

  const filterForSave = (data) => {
    const ret = {}
    for (const [field, value] of Object.entries(data.fields)) {
      if (value === '') {
        continue
      }
      if (value.startsWith(FK)) {
        continue
      }
      ret[field] = value
    }
    return ret
  }

  return {
    retrieveTableInfo,
    filterForSave,
    columnSettings: projectInfo?.columnSettings,
    fields
  }
}

export default useFieldMgr
