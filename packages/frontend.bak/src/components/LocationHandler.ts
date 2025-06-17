import {
  useEffect,
  FC,
  ReactNode
} from 'react'
import {
  useParams,
  useLocation
} from 'react-router-dom'

import useProject from '~/api/useProject'

type Props = {
  children: ReactNode
}

const LocationHandler: FC<Props> = ({ children }) => {
  const setCurrentPath = useProject(state => state.setCurrentPath)
  const updateDataList = useProject(state => state.updateDataList)
  const { id } = useParams()
  const { pathname } = useLocation()

  useEffect(() => {
    setCurrentPath(pathname)
    updateDataList(id)
  }, [setCurrentPath, updateDataList, id, pathname])

  return children
}

export default LocationHandler
