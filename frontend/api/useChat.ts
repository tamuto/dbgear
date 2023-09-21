import { useState } from 'react'
import axios from 'axios'
import useProject from './useProject'

type ChatParams = {
  make_json: (message: string) => object,
  response: (result: object) => void
}

const useChat = (params: ChatParams) => {
  const [skeleton, setSkeleton] = useState<boolean>(false)
  const proj = useProject(state => state.projectInfo)

  const chat = (message: string) => {
    if (message === '') {
      return
    }
    setSkeleton(true)
    const data = params.make_json(message)
    axios.post('https://api.openai.com/v1/chat/completions', data, {
      headers: {
        ['Content-Type']: 'application/json',
        Authorization: `Bearer ${proj!.apiKey}`
      }
    }).then(result => {
      params.response(result.data)
      setSkeleton(false)
    })
  }

  if (proj?.apiKey == null) {
    return {
      chat: null,
    }
  }

  return {
    chat,
    skeleton,
  }
}

export default useChat
