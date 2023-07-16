import { css } from '@emotion/react'
import {
  Box,
  Tabs,
  Tab,
  Typography
} from '@mui/material'

import TabPanel from './TabPanel'
import TemplateDataProperties from './TemplateDataProperties'
import TemplateDataEditor from './TemplateDataEditor'
import useTemplateDataTab from '../api/useTemplateDataTab'

const TemplateDataTab = () => {
  const roundHeadCss = css`
    position: relative;
    padding: 0.25em 0;
    &:after {
      content: '';
      display: block;
      height: 4px;
      background: -webkit-linear-gradient(to right, rgb(134, 204, 206), transparent);
      background: linear-gradient(to right, rgb(134, 204, 206), transparent);
    }
  `

  const {
    tabIndex,
    handleChange,
    a11yProps,
    data
  } = useTemplateDataTab()

  return (
    <Box>
      {
        data &&
        <Typography css={roundHeadCss} variant='h6' component='div'>
          {data.instance}.{data.info.tableName} ({data.info.displayName})
        </Typography>
      }
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabIndex} onChange={handleChange} aria-label='tabs'>
          <Tab label='Editor' {...a11yProps(0)} />
          <Tab label='Properties' {...a11yProps(1)} />
        </Tabs>
      </Box>
      <TabPanel value={tabIndex} index={0}>
        {
          data &&
          <TemplateDataEditor data={data} />
        }
      </TabPanel>
      <TabPanel value={tabIndex} index={1}>
        <TemplateDataProperties />
      </TabPanel>
    </Box>
  )
}

export default TemplateDataTab
