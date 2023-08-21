import { Outlet } from 'react-router-dom'
import {
  Box,
  Tabs,
  Tab,
} from '@mui/material'
import Head from '~/cmp/Head'
import useDataTab from '../api/useDataTab'

const DataTab = () => {
  const {
    tabIndex,
    handleChange,
    data
  } = useDataTab()

  return (
    <Box>
      {
        data &&
        <Head title={`${data.model.instance}.${data.model.tableName} (${data.table.displayName})`} />
      }
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabIndex} onChange={handleChange} aria-label='tabs'>
          <Tab label='Editor' value='_data' />
          <Tab label='Properties' value='_props' />
        </Tabs>
      </Box>
      <Box sx={{ pt: 2 }}>
        {
          data &&
          <Outlet context={{ data }} />
        }
      </Box>
    </Box>
  )
}

export default DataTab
