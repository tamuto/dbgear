import { css } from '@emotion/react'
import { useNavigate, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  Stack
} from '@mui/material'
import Head from '~/cmp/Head'
import Description from '~/cmp/Description'

import useProject from '~/api/useProject'

const tableCss = css`
.entity {
  width: 250px;
}
.entity span {
  display: block;
}
.entity .displayName {
  font-size: 0.8em;
  color: #999;
}
.entity .displayName::before {
  content: '(';
}
.entity .displayName::after {
  content: ')';
}
.description {
}
`

const EnvironPage = () => {
  const { t } = useTranslation()
  const dataList = useProject(state => state.dataList)
  const mapping = useProject(state => state.currentMapping)
  const { id } = useParams()
  const navigate = useNavigate()

  return (
    <Stack>
      <Head title={t('caption.managedData')} />
      {
        mapping &&
        <Description value={mapping.description} />
      }
      <TableContainer component={Paper}>
        <Table css={tableCss}>
          <TableHead>
            <TableRow>
              <TableCell className='name'>{t('caption.dataName')}</TableCell>
              <TableCell className='description'>{t('caption.description')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {
              dataList.map(item => (
                <TableRow
                  className='clickable'
                  key={item.tableName}
                  onClick={() => navigate(`/environs/${id}/${item.instance}/${item.tableName}/_data`)}
                >
                  <TableCell className='entity'>
                    <span className='entity'>{item.instance}.{item.tableName}</span>
                    <span className='displayName'>{item.displayName}</span>
                  </TableCell>
                  <TableCell className='description'><Description value={item.description} /></TableCell>
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
