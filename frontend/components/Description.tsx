import { FC } from 'react'
import {
  Typography,
} from '@mui/material'

type DescriptionProps = {
  value: string
}

const Description: FC<DescriptionProps> = ({ value }) => {
  return (
    <Typography>
      <span dangerouslySetInnerHTML={{ __html: value }}></span>
    </Typography>
  )
}

export default Description
