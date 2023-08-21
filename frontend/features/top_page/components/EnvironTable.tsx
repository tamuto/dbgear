import { css } from '@emotion/react'
import { useNavigate } from 'react-router-dom'
import {
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Typography,
  Paper,
  Stack
} from '@mui/material'
import Head from '~/cmp/Head'

import useProject from '~/api/useProject'

const tableCss = css`
.id {
  width: 120px;
}
.name {
  width: 250px;
}
.description {
}
`

const EnvironListPage = () => {
  const environs = useProject(state => state.environs)
  const info = useProject(state => state.projectInfo)
  const navigate = useNavigate()

  return (
    <Stack>
      <Head title='Environs' />
      {
        info &&
        <Typography><span dangerouslySetInnerHTML={{ __html: info.description }}></span></Typography>
      }
      <TableContainer component={Paper}>
        <Table css={tableCss}>
          <TableHead>
            <TableRow>
              <TableCell className='id'>ID</TableCell>
              <TableCell className='name'>Name</TableCell>
              <TableCell className='description'>Description</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {
              environs.map(item => (
                <TableRow className='clickable' key={item.id} onClick={() => navigate(`/environs/${item.id}`)}>
                  {/* TODO 配布可能ならアイコンとかで表示する。 */}
                  <TableCell className='id'>{item.id}</TableCell>
                  <TableCell className='name'>{item.name}</TableCell>
                  <TableCell className='description'>{item.description}</TableCell>
                </TableRow>
              ))
            }
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  )
}

export default EnvironListPage
