import { FC } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Stack,
  MenuItem
} from '@mui/material'
import {
  HookFormField
} from '@infodb/uilib'
import PublishedWithChangesIcon from '@mui/icons-material/PublishedWithChanges'
import useImportSQL from '../api/useImportSQL'

type ImpotSQLButtonProps = {
  disabledAppendAndRemove: boolean,
  segment: string | null
}

const ImpotSQLButton: FC<ImpotSQLButtonProps> = ({ disabledAppendAndRemove, segment }) => {
  const { t } = useTranslation()
  const { setOpen, open, control, onSubmit } = useImportSQL(segment)

  return (
    <>
      <Button
        size='small'
        color='secondary'
        startIcon={<PublishedWithChangesIcon />}
        disabled={disabledAppendAndRemove}
        onClick={() => setOpen(true)}
      >
        {t('caption.import')}
      </Button>
      <Dialog
        component='form'
        open={open}
        onClose={() => setOpen(false)}
        onSubmit={onSubmit}
      >
        <DialogTitle>{t('caption.importSQL')}</DialogTitle>
        <DialogContent>
          <DialogContentText>
            {t('message.importSQLDesc')}
          </DialogContentText>
          <Stack sx={{ mt: 2 }}>
            <HookFormField
              type='select'
              name='host'
              label={t('caption.host')}
              control={control}
            >
              <MenuItem value='localhost'>localhost</MenuItem>
            </HookFormField>
            <HookFormField
              type='multiline'
              name='sql'
              label={t('caption.sql')}
              control={control}
              rows={3}
            />
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
            {t('caption.import')}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default ImpotSQLButton
