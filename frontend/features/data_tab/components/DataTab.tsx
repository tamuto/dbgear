import { Outlet } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Box,
  Tabs,
  Tab,
} from '@mui/material'
import Head from '~/cmp/Head'
import Description from '~/cmp/Description'

import useDataTab from '../api/useDataTab'

const DataTab = () => {
  const { t } = useTranslation()
  const {
    tabIndex,
    handleChange,
    data,
    reload
  } = useDataTab()

  return (
    <Box>
      {
        data &&
        <>
          <Head title={`${data.model.instance}.${data.model.tableName} (${data.table.displayName})`} />
          <Description value={data.model.description} />
        </>
      }
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabIndex} onChange={handleChange} aria-label='tabs'>
          <Tab label={t('caption.editor')} value='_data' />
          <Tab label={t('caption.properties')} value='_props' />
        </Tabs>
      </Box>
      <Box sx={{ pt: 2 }}>
        {
          data &&
          <Outlet context={{ data, reload }} />
        }
      </Box>
    </Box>
  )
}

export default DataTab
