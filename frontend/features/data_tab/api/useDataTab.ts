import { useState, useEffect, useMemo, SyntheticEvent, useCallback } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import nxio from '~/api/nxio'

const useDataTab = () => {
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

  const reload = useCallback(async () => {
    nxio<Data>(`/environs/${id}/tables/${instance}/${table}`).get((result) => {
      console.log(result)
      setData(result)
    })
  }, [id, instance, table])

  useEffect(() => {
    reload()
  }, [reload])

  return {
    tabIndex,
    handleChange,
    data,
    reload
  }
}

export default useDataTab
