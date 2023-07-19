import PropTypes from 'prop-types'
import {
  Box,
  Button,
  Stack,
  Radio,
  FormControlLabel,
  Typography,
  MenuItem
} from '@mui/material'

import HookFormField from 'github://tamuto/uilib/components/form/HookFormField.js'
import FormFieldSet from 'github://tamuto/uilib/components/form/FormFieldSet.js'

import imgTable from '~/resources/img/table.png'
import imgMatrix from '~/resources/img/matrix.png'
import imgForm from '~/resources/img/form.png'

import ColumnSettingField from '~/components/ColumnSettingField'
import useTemplateDataSettings from '../api/useTemplateDataSettings'

const ImageLabel = ({ img, label }) => {
  return (
    <Box>
      <Typography component='div' variant='body2' sx={{ textAlign: 'center' }}>{label}</Typography>
      <img src={img} width='100px' />
    </Box>
  )
}
ImageLabel.propTypes = {
  img: PropTypes.string,
  label: PropTypes.string
}

const TemplateDataSettings = () => {
  const {
    control,
    onSubmit,
    layout,
    tableList,
    fields,
    columnSettings,
    editMode
  } = useTemplateDataSettings()
  return (
    <Stack component='form' onSubmit={onSubmit}>
      {
        !editMode &&
        <HookFormField type='select' label='Target Table' name='table' control={control}>
          {
            tableList.map(item => (
              <MenuItem key={item.tableName} value={`${item.instance}.${item.tableName}`}>
                {item.instance}.{item.tableName} ({item.displayName})
              </MenuItem>
            ))
          }
        </HookFormField>
      }
      <HookFormField type='radio' label='Input Form' name='layout' control={control} row={true}>
        <FormControlLabel value="table" control={<Radio />} label={<ImageLabel img={imgTable} label='Table' />} />
        <FormControlLabel value="matrix" control={<Radio />} label={<ImageLabel img={imgMatrix} label='Matrix' />} />
        <FormControlLabel value="single" control={<Radio />} label={<ImageLabel img={imgForm} label='SingleEntry' />} />
      </HookFormField>
      {
        layout === 'matrix' &&
        <p>Matrix UI</p>
      }
      {
        layout === 'single' &&
        <p>Single UI</p>
      }
      <FormFieldSet label='Column Settings'>
        {
          fields.map(item => (
            <ColumnSettingField
              key={item.key}
              control={control}
              item={item}
              settings={columnSettings} />
          ))
        }
      </FormFieldSet>
      <Box sx={{ textAlign: 'right' }}>
        <Button type='submit'>
          {
            editMode ? 'Update' : 'Create'
          }
        </Button>
      </Box>
    </Stack>
  )
}

export default TemplateDataSettings
