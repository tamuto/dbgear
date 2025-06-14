import { FC } from 'react'
import { useTranslation } from 'react-i18next'
import { Control } from 'react-hook-form'
import {
  Stack,
  MenuItem
} from '@mui/material'
import {
  HookFormField
} from '@infodb/uilib'

type ColumnSettingFieldProps = {
  control: Control<FormValues>,
  columnField: ColumnSettings,
  fieldItems: FieldItem[]
}

const ColumnSettingField: FC<ColumnSettingFieldProps> = ({ control, columnField, fieldItems }) => {
  const { t } = useTranslation()
  return (
    <Stack direction='row'>
      <div style={{ flexGrow: 1 }}>
        <HookFormField
          type='select'
          name={columnField.name}
          label={columnField.label}
          control={control}
        >
          <MenuItem value=''></MenuItem>
          {
            fieldItems.map(item => (
              <MenuItem key={item.value} value={item.value}>{item.caption}</MenuItem>
            ))
          }
        </HookFormField>
      </div>
      <HookFormField type='text' sx={{ width: 80 }} nolabel name={`${columnField.name}_width`} label={t('caption.width')} control={control} />
    </Stack>
  )
}

export default ColumnSettingField
