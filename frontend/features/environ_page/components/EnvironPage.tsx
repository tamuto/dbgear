import { css } from '@emotion/react'
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
.entity {
  width: 350px;
}
`

const EnvironPage = () => {
  const dataList = useProject(state => state.dataList)
  const mapping = useProject(state => state.currentMapping)

  return (
    <Stack>
      <Head title='Managed Data' />
      <Typography>{mapping?.description}</Typography>
      <TableContainer component={Paper}>
        <Table css={tableCss}>
          <TableHead>
            <TableRow>
              <TableCell className='entity'>Data Name</TableCell>
              <TableCell className='displayName'>Remarks</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {
              dataList.map(item => (
                <TableRow className='clickable' key={item.tableName} onClick={() => console.log('clicked')}>
                  <TableCell className='entity'>{item.instance}.{item.tableName}</TableCell>
                  <TableCell className='displayName'>{item.displayName}</TableCell>
                </TableRow>
              ))
            }
          </TableBody>
        </Table>
      </TableContainer>
    </Stack>
  )
}

export default EnvironPage
