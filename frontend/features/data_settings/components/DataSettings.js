import PropTypes from 'prop-types'
import {
  Box,
  Button,
  Stack,
  Radio,
  FormControlLabel,
  Typography
} from '@mui/material'

import HookFormField from 'github://tamuto/uilib/components/form/HookFormField.js'

import imgTable from '~/resources/img/table.png'
import imgMatrix from '~/resources/img/matrix.png'
import imgForm from '~/resources/img/form.png'
import useDataSettings from '../api/useDataSettings'

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

const DataSettings = () => {
  const { control, onSubmit, layout } = useDataSettings()
  return (
    <Stack component='form' onSubmit={onSubmit}>
      <HookFormField type='text' label='Target Table' name='table' control={control} />
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

export default DataSettings
