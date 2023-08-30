import {
  useOutletContext,
} from 'react-router-dom'
import DataSettings from './DataSettings'

const DataSettingsWrapper = () => {
  const { data, reload } = useOutletContext<{data: Data, reload: () => void}>()
  return (
    <DataSettings data={data} reload={reload} />
  )
}

export default DataSettingsWrapper
