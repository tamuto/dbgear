import { ChangeEvent, KeyboardEvent, FC, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { css } from '@emotion/react'
import {
  Box,
  IconButton,
  TextField,
  Stack,
  Paper
} from '@mui/material'
import SendIcon from '@mui/icons-material/Send'

import ChatMessage from './ChatMessage'

const ChatCss = css`
  width: 550px;
  height: 565px;
  margin: 16px 16px 16px 0;
  position: relative;

  .chat {
    height: calc(100% - 60px);
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 8px;
    overflow-y: auto;
    margin-bottom: 8px;
  }

  .input {
    width: 100%;
    padding: 8px;
    background-color: #efe;
  }
`

type ChatBoxProps = {
  messages: Message[],
  chat: ((message: string) => void) | null,
  skeleton?: boolean | undefined
}

const ChatBox: FC<ChatBoxProps> = ({ messages, chat, skeleton }) => {
  const { t } = useTranslation()
  const [message, setMessage] = useState('')
  const onChange = (e: ChangeEvent<HTMLInputElement>) => setMessage(e.target.value)
  const onSendMessage = () => {
    if (chat) {
      chat(message)
    }
    setMessage('')
  }
  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => { if (e.key === 'Enter') { onSendMessage(); e.preventDefault() } }

  return (
    <Box css={ChatCss}>
      <Stack className='chat'>
        {
          messages.filter(x => x.role !== 'system').map((message, index) => (
            <ChatMessage key={index} role={message.role} content={message.content} />
          ))
        }
        {
          skeleton &&
          <ChatMessage role='skeleton' content='' />
        }
      </Stack>
      <Paper className='input' component={Stack} direction='row' elevation={3}>
        <TextField
          label={t('caption.message')}
          fullWidth
          value={message}
          onChange={onChange}
          onKeyDown={onKeyDown}
        />
        <IconButton onClick={onSendMessage}>
          <SendIcon />
        </IconButton>
      </Paper>
    </Box>
  )
}

export default ChatBox
