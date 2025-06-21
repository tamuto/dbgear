import { FC } from 'react'
import { css } from '@emotion/react'
import {
  Typography
} from '@mui/material'

const headCss = css`
position: relative;
padding: 0.25em 0;
&:after {
  content: '';
  display: block;
  height: 4px;
  background: -webkit-linear-gradient(to right, rgb(134, 204, 206), transparent);
  background: linear-gradient(to right, rgb(134, 204, 206), transparent);
}
`

type HeadProps = {
  title: string
}

const Head: FC<HeadProps> = ({ title }) => {
  return (
    <Typography variant='h6' css={headCss}>{title}</Typography>
  )
}

export default Head
