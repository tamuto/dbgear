import { css } from '@emotion/react'
import { Outlet } from 'react-router-dom'
import {
  Box,
  Tabs,
  Tab,
  Typography
} from '@mui/material'

import useTemplateDataTab from '../api/useTemplateDataTab'

const TemplateDataTab = () => {
  const headCss = css`
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
    data
  } = useTemplateDataTab()

  return (
    <Box>
      {
        data &&
        <Typography css={headCss} variant='h6' component='div'>
          {data.instance}.{data.info.tableName} ({data.info.displayName})
        </Typography>
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
          <Outlet context={data} />
        }
      </Box>
    </Box>
  )
}

export default TemplateDataTab
