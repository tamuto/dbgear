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
  const info = useProject(state => state.projectInfo)
  const environs = useProject(state => state.environs)
  const { control, onSubmit } = useEnvironSettings()

  return (
    <Stack component='form' onSubmit={onSubmit}>
      <Head title='Environ Settings' />
      <HookFormField type='text' name='id' label='Environ ID' control={control} />
      <HookFormField type='text' name='name' label='Environ Name' control={control} />
      <HookFormField type='select' name='base' label='Base Environ' control={control}>
        <MenuItem value=''></MenuItem>
        {
          environs.map(environ => (
            <MenuItem key={environ.id} value={environ.id}>{environ.name}</MenuItem>
          ))
        }
      </HookFormField>
      <HookFormField type='multiline' rows={3} name='description' label='Description' control={control} />
      <HookFormField type='select' name='instance' label='Instance' control={control}>
        {
          info?.instances.map(instance => (
            <MenuItem key={instance} value={instance}>{instance}</MenuItem>
          ))
        }
        {
          !info && <MenuItem value=''></MenuItem>
        }
      </HookFormField>
      <HookFormField type='switch' name='deployment' label='Deploymentable' control={control} />
      <Box sx={{ textAlign: 'right' }}>
        <Button type='submit'>Create</Button>
      </Box>
    </Stack>
  )
}

export default EnvironSettings
