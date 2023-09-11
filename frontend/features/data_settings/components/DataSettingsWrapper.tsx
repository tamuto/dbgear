import {
  useOutletContext,
} from 'react-router-dom'
import DataSettings from './DataSettings'

const DataSettingsWrapper = () => {
  const { data, reload } = useOutletContext<{data: Data, reload: (segment: string | null) => void}>()
  return (
    <DataSettings data={data} reload={reload} />
  )
}

export default DataSettingsWrapper
