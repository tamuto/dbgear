import { FC } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Box,
  Button,
  Stack,
  Radio,
  FormControlLabel,
  Typography,
  MenuItem
} from '@mui/material'
import {
  HookFormField,
  FormFieldSet,
} from '@infodb/uilib'
import Head from '~/cmp/Head'

import imgTable from '~/img/table.png'
import imgMatrix from '~/img/matrix.png'
import imgForm from '~/img/form.png'

import ColumnSettingField from './ColumnSettingField'
import ImageLabel from './ImageLabel'
import useDataSettings from '../api/useDataSettings'

type DataSettingsProps = {
  data: Data | null
}

const DataSettings: FC<DataSettingsProps> = ({ data }) => {
  const { t } = useTranslation()
  const {
    control,
    onSubmit,
    layout,
    tableList,
    columnFields,
    fieldItems,
    editMode
  } = useDataSettings(data)
  return (
    <Stack component='form' onSubmit={onSubmit}>
      {
        !editMode &&
        <>
          <Head title={t('caption.addData')} />
          <HookFormField type='select' label={t('caption.targetTable')} name='table' control={control}>
            {
              tableList.map(item => (
                <MenuItem key={item.tableName} value={`${item.instance}.${item.tableName}`}>
                  {item.instance}.{item.tableName} ({item.displayName})
                </MenuItem>
              ))
            }
          </HookFormField>
        </>
      }
      <HookFormField type='multiline' label={t('caption.description')} name='description' control={control} rows={5} />
      <HookFormField type='select' label={t('caption.syncMode')} name='syncMode' control={control}>
        <MenuItem value='drop_create'>{t('caption.dropCreate')}</MenuItem>
        <MenuItem value='update_diff'>{t('caption.updateDiff')}</MenuItem>
      </HookFormField>
      <FormFieldSet label={t('caption.forListDisplay')}>
        <Typography variant='body2' color='text.secondary'>{t('message.listDisplayDesc')}</Typography>
        <HookFormField type='select' label={t('caption.valueField')} name='value' control={control}>
          {
            columnFields.map(item => (
              <MenuItem key={item.key} value={item.name}>{item.label}</MenuItem>
            ))
          }
        </HookFormField>
        <HookFormField type='select' label={t('caption.captionField')} name='caption' control={control}>
          {
            columnFields.map(item => (
              <MenuItem key={item.key} value={item.name}>{item.label}</MenuItem>
            ))
          }
        </HookFormField>
      </FormFieldSet>
      <FormFieldSet label={t('caption.inputForm')}>
        <Typography variant='body2' color='text.secondary'>{t('message.inputFormDesc')}</Typography>
        <HookFormField type='radio' label={t('caption.layout')} name='layout' control={control} row={true}>
          <FormControlLabel value="table" control={<Radio />} label={<ImageLabel img={imgTable} label={t('caption.table')} />} />
          <FormControlLabel value="matrix" control={<Radio />} label={<ImageLabel img={imgMatrix} label={t('caption.matrix')} />} />
          <FormControlLabel value="single" control={<Radio />} label={<ImageLabel img={imgForm} label={t('caption.singleEntry')} />} />
        </HookFormField>
        {
          layout === 'matrix' &&
          <HookFormField type='select' label={t('caption.xAxis')} name='x_axis' control={control}>
            {
              columnFields.map(item => (
                <MenuItem key={item.key} value={item.name}>{item.label}</MenuItem>
              ))
            }
          </HookFormField>
        }
        {
          ['matrix', 'single'].includes(layout) &&
          <>
            <HookFormField type='select' label={t('caption.yAxis')} name='y_axis' control={control}>
              {
                columnFields.map(item => (
                  <MenuItem key={item.key} value={item.name}>{item.label}</MenuItem>
                ))
              }
            </HookFormField>
            <HookFormField type='select' label={t('caption.cells')} name='cells' control={control}>
              {
                columnFields.map(item => (
                  <MenuItem key={item.key} value={item.name}>{item.label}</MenuItem>
                ))
              }
            </HookFormField>
          </>
        }
      </FormFieldSet>
      <FormFieldSet label={t('caption.columnSettings')}>
        {
          columnFields.map(item => (
            <ColumnSettingField
              key={item.key}
              control={control}
              columnField={item}
              fieldItems={fieldItems} />
          ))
        }
      </FormFieldSet>
      <Box sx={{ textAlign: 'right' }}>
        <Button type='submit'>
          {
            editMode ? t('caption.update') : t('caption.create')
          }
        </Button>
      </Box>
    </Stack>
  )
}

export default DataSettings
