import {
  useOutletContext,
} from 'react-router-dom'
import DataSettings from './DataSettings'

const DataSettingsWrapper = () => {
  const { data } = useOutletContext<{data: Data}>()
  return (
    <DataSettings data={data} />
  )
}

export default DataSettingsWrapper
