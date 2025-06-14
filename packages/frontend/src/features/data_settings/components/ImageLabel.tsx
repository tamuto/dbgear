import { FC } from 'react'
import {
  Box,
  Typography
} from '@mui/material'

type ImageLabelProps = {
  img: string
  label: string
}

const ImageLabel: FC<ImageLabelProps> = ({ img, label }) => {
  return (
    <Box>
      <Typography component='div' variant='body2' sx={{ textAlign: 'center' }}>{label}</Typography>
      <img src={img} width='100px' />
    </Box>
  )
}

export default ImageLabel
