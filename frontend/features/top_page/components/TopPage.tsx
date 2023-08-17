import {
  Stack
} from '@mui/material'
import EnvironTable from './EnvironTable'
import DeploymentTable from './DeploymentTable'

const TopPage = () => {
  return (
    <Stack>
      <EnvironTable />
      <DeploymentTable />
    </Stack>
  )
}

export default TopPage
