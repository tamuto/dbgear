import PropTypes from 'prop-types'
import {
  Box
} from '@mui/material'

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
TabPanel.propTypes = {
  children: PropTypes.node,
  value: PropTypes.number,
  index: PropTypes.number
}

export default TabPanel
