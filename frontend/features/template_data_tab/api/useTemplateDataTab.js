import { useEffect, useState, useMemo } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import axios from 'axios'

import useProject from '~/api/useProject'

const useTemplateDataTab = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const { id, instance, tableName } = useParams()

  const tabIndex = useMemo(() => {
    const sp = location.pathname.split('/')
    return sp[sp.length - 1]
  }, [location.pathname])

  const handleChange = (e, newValue) => {
    navigate(`/templates/${id}/${instance}/${tableName}/${newValue}`)
  }

  const _init = async () => {
    const result = await axios.get(`/templates/${id}/${instance}/${tableName}`)
    setData(result.data)
  }

  useEffect(() => {
    _init()
  }, [id, instance, tableName])

  return {
    tabIndex,
    handleChange,
    data
  }
}

export default useTemplateDataTab
