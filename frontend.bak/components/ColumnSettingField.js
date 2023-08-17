import PropTypes from 'prop-types'
import {
  MenuItem
} from "@mui/material"
import HookFormField from 'github://tamuto/uilib/components/form/HookFormField.js'

const ColumnSettingField = ({ control, item, settings }) => {
  if (item.type === 'select') {
    return (
      <HookFormField {...item} control={control}>
        <MenuItem value=''></MenuItem>
        {
          settings.map(item => (
            <MenuItem key={item.value} value={item.value}>{item.value}</MenuItem>
          ))
        }
      </HookFormField>
    )
  }
  return <HookFormField {...item} control={control} readonly />
}
ColumnSettingField.propTypes = {
  item: PropTypes.object,
  settings: PropTypes.array
}

export default ColumnSettingField
