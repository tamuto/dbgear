import { useState } from 'react'
import {
  Box,
  Tabs,
  Tab
} from '@mui/material'

const TemplateDataTab = () => {
  function a11yProps(index) {
    return {
      id: `template-data-tab-${index}`,
      'aria-controls': 'template-data-tabpanel-${index}'
    }
  }
  const TabPanel = ({ children, value, index, ...pros }) => {
    return (
      <div
        role='tabpanel'
        hidden={value !== index}
        id={`template-data-tabpanel-${index}`}
        aria-labelledby={`template-data-tab-${index}`}
        {...pros}
      >
        {
          value === index &&
          <Box sx={{ p: 2 }}>
            {children}
          </Box>
        }
      </div>
    )
  }

  const [value, setValue] = useState(0)
  const handleChange = (e, newValue) => {
    setValue(newValue)
  }

  return (
    <Box>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={value} onChange={handleChange} aria-label='tabs'>
          <Tab label='Editor' {...a11yProps(0)} />
          <Tab label='Propeties' {...a11yProps(1)} />
        </Tabs>
      </Box>
      <TabPanel value={value} index={0}>
        <p>エディタ</p>
      </TabPanel>
      <TabPanel value={value} index={1}>
        <p>プロパティ</p>
      </TabPanel>
    </Box>
  )
}

export default TemplateDataTab
