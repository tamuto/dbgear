import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import useProject from '../api/useProject'

const LocationHandler = ({ children }) => {
  const location = useLocation()
  const setCurrentPath = useProject(state => state.setCurrentPath)

  useEffect(() => {
    setCurrentPath(location.pathname)
  }, [location.pathname])

  return children
}

export default LocationHandler
