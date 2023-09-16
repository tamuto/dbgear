import { FC } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  MenuItem,
  Stack
} from '@mui/material'
import {
  HookFormField
} from '@infodb/uilib'

import DynamicFormIcon from '@mui/icons-material/DynamicForm'

import useFillData from '../api/useFillData'

type FillDataButtonProps = {
  columns: GridColumn[],
  fillData: (column: string, value: string) => void
}

const FillDataButton: FC<FillDataButtonProps> = ({ columns, fillData }) => {
  const { t } = useTranslation()
  const {
    setOpen,
    open,
    control,
    onSubmit,
    valueType,
    items
  } = useFillData(columns, fillData)

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
        component='form'
        open={open}
        onClose={() => setOpen(false)}
        onSubmit={onSubmit}
      >
        <DialogTitle>{t('caption.fillData')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('message.fillDataDesc')}
          </DialogContentText>
          <Stack sx={{ mt: 2 }}>
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
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button
            onClick={() => setOpen(false)}
            color='inherit'
          >
            {t('caption.cancel')}
          </Button>
          <Button
            type='submit'
            color='primary'
          >
            {t('caption.fillData')}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default FillDataButton
