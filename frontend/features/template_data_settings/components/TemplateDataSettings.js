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

import imgTable from '~/resources/img/table.png'
import imgMatrix from '~/resources/img/matrix.png'
import imgForm from '~/resources/img/form.png'
import useDataSettings from '../api/useTemplateDataSettings'

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
  const { control, onSubmit, layout, tableList } = useDataSettings()
  return (
    <Stack component='form' onSubmit={onSubmit}>
      <HookFormField type='select' label='Target Table' name='table' control={control}>
        {
          tableList.map(item => (
            <MenuItem key={item.tableName} value={`${item.instance}.${item.tableName}`}>
              {item.instance}.{item.tableName} ({item.displayName})
            </MenuItem>
          ))
        }
      </HookFormField>
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
      <Box sx={{ textAlign: 'right' }}>
        <Button type='submit'>Create</Button>
      </Box>
    </Stack>
  )
}

export default TemplateDataSettings