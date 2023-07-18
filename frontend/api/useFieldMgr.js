import { useState } from 'react'
import axios from 'axios'
import useProject from './useProject'

const useFieldMgr = (setValue, unregister) => {
  const projectInfo = useProject(state => state.projectInfo)
  const [fields, setFields] = useState([])

  const _buildField = (tableInfo) => {
    const makeFieldName = (field) => `fields.${field.columnName}`
    const judgeDefvalue = (field) => {
      if (field.foreignKey !== null) {
        return `Foreing Key: ${field.foreignKey}`
      }
      if (field.columnName in projectInfo.rules) {
        return projectInfo.rules[field.columnName]
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

  const retrieve_table_info = async (table) => {
    if (table === '') {
      return
    }
    const [instance, tableName] = table.split('.')
    const result = await axios.get(`/tables/${instance}/${tableName}`)
    const newFields = _buildField(result.data)
    _resetFields(newFields)
    setFields(newFields)
  }

  return {
    retrieve_table_info,
    columnSettings: projectInfo?.columnSettings,
    fields
  }
}

export default useFieldMgr
