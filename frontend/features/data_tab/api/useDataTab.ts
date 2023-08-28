import { useState, useEffect, useMemo, SyntheticEvent } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import useAxios from '~/api/useAxios'

const useDataTab = () => {
  const axios = useAxios()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { id, instance, table } = useParams()

  const tabIndex = useMemo(() => {
    const sp = pathname.split('/')
    return sp[sp.length - 1]
  }, [pathname])

  const handleChange = (e: SyntheticEvent, newValue: string) => {
    navigate(`/environs/${id}/${instance}/${table}/${newValue}`)
  }

  const [data, setData] = useState<Data|null>(null)

  useEffect(() => {
    axios<Data>(`/environs/${id}/tables/${instance}/${table}`).get((result) => {
      console.log(result)
      setData(result)
    })
  }, [id, instance, table])

  return {
    tabIndex,
    handleChange,
    data,
  }
}

export default useDataTab
