import { useTranslation } from 'react-i18next'
import {
  Stack,
  MenuItem,
  Box,
  Button,
} from '@mui/material'
import {
  HookFormField
} from '@infodb/uilib'
import Head from '~/cmp/Head'
import useEnvironSettings from '../api/useEnvironSettings'
import useProject from '~/api/useProject'

const EnvironSettings = () => {
  const { t } = useTranslation()
  const info = useProject(state => state.projectInfo)
  const environs = useProject(state => state.environs)
  const { control, onSubmit } = useEnvironSettings()

  return (
    <Stack component='form' onSubmit={onSubmit}>
      <Head title={t('caption.environSettings')} />
      <HookFormField
        type='text'
        name='group'
        label={t('caption.environGroup')}
        control={control}
      />
      <HookFormField
        type='text'
        name='id'
        label={t('caption.environID')}
        control={control}
        rules={{ required: t('message.required') }}
      />
      <HookFormField
        type='text'
        name='name'
        label={t('caption.environName')}
        control={control}
        rules={{ required: t('message.required') }}
      />
      <HookFormField type='select' name='base' label={t('caption.baseEnviron')} control={control}>
        <MenuItem value=''></MenuItem>
        {
          environs.flatMap(x => x.children).map(environ => (
            <MenuItem key={environ.id} value={environ.id}>{environ.group} / {environ.name}</MenuItem>
          ))
        }
      </HookFormField>
      <HookFormField type='multiline' rows={3} name='description' label={t('caption.description')} control={control} />
      <HookFormField
        type='select'
        name='instances'
        label={t('caption.instances')}
        control={control}
        rules={{ required: t('message.required') }}
        SelectProps={{ multiple: true }}
      >
        {
          info?.instances.map(instance => (
            <MenuItem key={instance} value={instance}>{instance}</MenuItem>
          ))
        }
        {
          !info && <MenuItem value=''></MenuItem>
        }
      </HookFormField>
      <HookFormField type='switch' name='deployment' label={t('caption.deploymentable')} control={control} />
      <Box sx={{ textAlign: 'right' }}>
        <Button type='submit'>Create</Button>
      </Box>
    </Stack>
  )
}

export default EnvironSettings
