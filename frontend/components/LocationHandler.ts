import {
  useEffect,
  FC,
  ReactNode
} from 'react'
import { useLocation } from 'react-router-dom'

import useProject from '~/api/useProject'

type Props = {
  children: ReactNode
}

const LocationHandler: FC<Props> = ({ children }) => {
  const location = useLocation()
  const setCurrentPath = useProject(state => state.setCurrentPath)

  useEffect(() => {
    setCurrentPath(location.pathname)
  }, [location.pathname])

  return children
}

export default LocationHandler
