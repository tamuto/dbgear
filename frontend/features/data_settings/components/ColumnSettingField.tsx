import { FC } from 'react'
import {
  MenuItem
} from '@mui/material'
import {
  HookFormField
} from '@infodb/uilib'

type ColumnSettingFieldProps = {
  control: any,
  columnField: ColumnSettings,
  fieldItems: FieldItem[]
}

const ColumnSettingField: FC<ColumnSettingFieldProps> = ({ control, columnField, fieldItems }) => {
  return (
    <HookFormField type='select' {...columnField} control={control}>
      <MenuItem value=''></MenuItem>
      {
        fieldItems.map(item => (
          <MenuItem key={item.value} value={item.value}>{item.caption}</MenuItem>
        ))
      }
    </HookFormField>
  )
}

export default ColumnSettingField
