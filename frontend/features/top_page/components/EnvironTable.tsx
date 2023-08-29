import { css } from '@emotion/react'
import { useNavigate } from 'react-router-dom'
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
.name {
  width: 250px;
}
.name span {
  display: block;
}
.name .id {
  font-size: 0.8em;
  color: #999;
}
.name .id::before {
  content: '(';
}
.name .id::after {
  content: ')';
}
.description {
}
`

const EnvironListPage = () => {
  const { t } = useTranslation()
  const environs = useProject(state => state.environs)
  const info = useProject(state => state.projectInfo)
  const navigate = useNavigate()

  return (
    <Stack>
      <Head title={t('caption.environs')} />
      {
        info &&
        <Description value={info.description} />
      }
      <TableContainer component={Paper}>
        <Table css={tableCss}>
          <TableHead>
            <TableRow>
              <TableCell className='name'>{t('caption.environName')}</TableCell>
              <TableCell className='description'>{t('caption.description')}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {
              environs.flatMap(x => x.children).map(item => (
                <TableRow className='clickable' key={item.id} onClick={() => navigate(`/environs/${item.id}`)}>
                  {/* TODO 配布可能ならアイコンとかで表示する。 */}
                  <TableCell className='name'>
                    <span className='name'>{item.group} / {item.name}</span>
                    <span className='id'>{item.id}</span>
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

export default EnvironListPage
