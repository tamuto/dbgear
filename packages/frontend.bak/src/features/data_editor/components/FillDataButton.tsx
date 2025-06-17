import { FC } from 'react'
import { css } from '@emotion/react'
import { useTranslation } from 'react-i18next'
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  MenuItem,
  Stack,
  FormControlLabel,
  Radio,
  FormHelperText
} from '@mui/material'
import {
  FormFieldSet,
  HookFormField
} from '@infodb/uilib'

import DynamicFormIcon from '@mui/icons-material/DynamicForm'

import useFillData from '../api/useFillData'
import ChatBox from '~/cmp/ChatBox'

type FillDataButtonProps = {
  columns: GridColumn[],
  rowCount: number,
  fillData: (method: string, column: string, value: string) => void
}

const DialogCss = css`
.MuiDialog-paper {
  max-width: unset;
}
`

const FillDataButton: FC<FillDataButtonProps> = ({ columns, rowCount, fillData }) => {
  const { t } = useTranslation()
  const {
    setOpen,
    open,
    control,
    onSubmit,
    valueType,
    items,
    method,
    needLine,
    applyChat,
  } = useFillData(columns, rowCount, fillData)

  return (
    <>
      <Button
        size='small'
        startIcon={<DynamicFormIcon />}
        onClick={() => setOpen(true)}
      >
        {t('caption.fillData')}
      </Button>
      <Dialog
        css={DialogCss}
        component='form'
        open={open}
        onClose={() => setOpen(false)}
        onSubmit={onSubmit}
      >
        <Stack direction='row' spacing={0}>
          <div>
            <DialogTitle>{t('caption.fillData')}</DialogTitle>
            <DialogContent>
              <DialogContentText>
                {t('message.fillDataDesc')}
              </DialogContentText>
              <Stack sx={{ mt: 2 }}>
                <HookFormField type='radio' name='method' label='入力方法' control={control} row={true}>
                  <FormControlLabel value='single' control={<Radio />} label='単一入力' />
                  <FormControlLabel value='multiple' control={<Radio />} label='複数入力' />
                  <FormControlLabel value='ai' control={<Radio />} label='AIサポート' />
                </HookFormField>
                {
                  method === 'single' && (
                    <>
                      <HookFormField
                        type='select'
                        name='column'
                        label={t('caption.fillDataColumn')}
                        control={control}
                        rules={{ required: t('message.required') }}
                      >
                        {
                          columns.filter(x => x.editable).map((column) => (
                            <MenuItem key={column.field} value={column.field}>
                              {column.headerName}
                            </MenuItem>
                          ))
                        }
                      </HookFormField>
                      <HookFormField
                        type={valueType}
                        name='value'
                        label={t('caption.fillDataValue')}
                        control={control}
                      >
                        <MenuItem value=''></MenuItem>
                        {
                          items.map((item) => (
                            <MenuItem key={item.value} value={item.value}>
                              {item.caption}
                            </MenuItem>
                          ))
                        }
                      </HookFormField>
                    </>
                  )
                }
                {
                  ['multiple', 'ai'].includes(method) && (
                    <>
                      <HookFormField
                        type='select'
                        name='column'
                        label={t('caption.fillDataColumn')}
                        control={control}
                        rules={{ required: t('message.required') }}
                      >
                        {
                          columns.filter(x => x.editable).map((column) => (
                            <MenuItem key={column.field} value={column.field}>
                              {column.headerName}
                            </MenuItem>
                          ))
                        }
                      </HookFormField>
                      <HookFormField
                        type='multiline'
                        name='value'
                        label={t('caption.fillDataValue')}
                        control={control}
                        rows={13}
                      />
                      <FormFieldSet>
                        <FormHelperText>{needLine}</FormHelperText>
                      </FormFieldSet>
                    </>
                  )
                }
              </Stack>
            </DialogContent>
            <DialogActions>
              <Button
                onClick={() => setOpen(false)}
                color='inherit'
              >
                {t('caption.close')}
              </Button>
              <Button
                type='submit'
                color='primary'
              >
                {t('caption.fillData')}
              </Button>
            </DialogActions>
          </div>
          {
            method === 'ai' && (
              <ChatBox {...applyChat} />
            )
          }
        </Stack>
      </Dialog>
    </>
  )
}

export default FillDataButton
