import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'

const useTemplateDataTab = () => {
  const [data, setData] = useState(null)
  const [tabIndex, setTabIndex] = useState(0)
  const { id, instance, tableName} = useParams()

  const handleChange = (e, newValue) => {
    setTabIndex(newValue)
  }

  const a11yProps = (index) => {
    return {
      id: `template-data-tab-${index}`,
      'aria-controls': 'template-data-tabpanel-${index}'
    }
  }

  const _init = async () => {
    const result = await axios.get(`/templates/${id}/${instance}/${tableName}`)
    console.log(result.data)
    setData(result.data)
  }

  useEffect(() => {
    _init()
  }, [id, instance, tableName])

  return {
    tabIndex,
    handleChange,
    a11yProps,
    data
  }

}

export default useTemplateDataTab
