import { createRoot } from 'react-dom/client'
import DataEditor from './features/editdata/components/DataEditor'

const root = createRoot(document.getElementById('app'))
root.render(
  <DataEditor />
)
