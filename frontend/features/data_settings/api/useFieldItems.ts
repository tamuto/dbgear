import { useEffect, useState } from 'react'

import useProject from '~/api/useProject'
import { FK } from './const'

const useFiedlItems = () => {
  const projectInfo = useProject(state => state.projectInfo)
  const refs = useProject(state => state.refs)
  const [fieldItems, setFieldItems] = useState<FieldItem[]>([])

  useEffect(() => {
    const data = [
      ...Object.keys(projectInfo!.bindings).map(key => {
        const item: FieldItem = {
          value: key,
          caption: projectInfo!.bindings[key].value,
        }
        return item
      }),
      ...refs.map(data => {
        const item: FieldItem = {
          value: `${FK}:${data.id}/${data.instance}.${data.tableName}`,
          caption: `${data.idName}/${data.instance}.${data.tableName} (${data.displayName})`,
        }
        return item
      }).sort((a, b) => { return a.caption.localeCompare(b.caption) })
    ]
    setFieldItems(data)
  }, [])

  return {
    fieldItems
  }
}

export default useFiedlItems
