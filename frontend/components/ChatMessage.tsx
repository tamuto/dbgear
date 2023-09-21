import { FC } from 'react'
import {
  Paper,
  Avatar,
  Stack,
  Typography,
  Skeleton
} from '@mui/material'
import PersonIcon from '@mui/icons-material/Person'
import Description from './Description'

const ChatMessage: FC<Message> = ({ role, content }) => {
  if (role === 'skeleton') {
    return (
      <Paper sx={{ p: 1 }} component={Stack} direction='row'>
        <Skeleton variant='circular'>
          <Avatar />
        </Skeleton>
        <Typography><Skeleton width={350} /></Typography>
      </Paper>
    )
  }

  return (
    <Paper sx={{ p: 1 }} component={Stack} direction='row'>
      {
        role === 'user' &&
        <Avatar sx={{ bgcolor: '#4169e1', color: 'white' }}>
          <PersonIcon />
        </Avatar>
      }
      {
        role === 'assistant' &&
        <Avatar sx={{ bgcolor: '#ff69b4', color: 'white' }}>AI</Avatar>
      }
      <Typography><Description value={content} /></Typography>
    </Paper>
  )
}

export default ChatMessage
