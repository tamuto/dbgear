import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { useForm } from 'react-hook-form'

import useChat from '~/api/useChat'

const useFillData = (columns: GridColumn[], fillData: (column: string, value: string) => void) => {
  const { t } = useTranslation()
  const [open, setOpen] = useState(false)
  const { control, handleSubmit, setValue, watch } = useForm({
    defaultValues: {
      method: 'single',
      column: '',
      value: '',
    }
  })
  const [column, method] = watch(['column', 'method'])
  const [valueType, setValueType] = useState('text')
  const [items, setItems] = useState<ListItem[]>([])
  const [messages, setMessages] = useState<Message[]>([])

  const make_json = (message: string) => {
    setMessages([
      ...messages,
      {
        role: 'user',
        content: message
      }
    ])
    function hasMessages(obj: object): obj is Record<'messages', Message[]> {
      return 'messages' in obj
    }

    const prompt = t('prompt.fillData', {returnObjects: true})
    if (hasMessages(prompt)) {
      const msg: Message[] = prompt.messages
      msg[0].content = msg[0].content.replace('{replace}', columns.map(x => `* ${x.headerName} (${x.field})`).join('\n'))
      msg[0].content = msg[0].content.replace('{nn}', '10')
      for (const m of messages) {
        msg.push(m)
      }
    }
    console.log(prompt)
    return prompt
  }

  const chatResult = (result: object) => {
    console.log(result)
    function hasChoices(obj: object): obj is Record<'choices', Choices[]> {
      return 'choices' in obj
    }
    if (hasChoices(result)) {
      const message = result.choices[0].message
      if (message.content) {
        setMessages(old => ([
          ...old,
          {
            role: 'assistant',
            content: message.content
          } as Message
        ]))
      }
      if (message.function_call) {
        if (message.function_call.name === 'setData') {
          const args = JSON.parse(message.function_call.arguments)
          setValue('column', args.column)
          setValue('value', args.data.replace('\\n', '\n'))
        }
      }
    }
  }

  const { chat, skeleton } = useChat({make_json, response: chatResult})

  useEffect(() => {
    setValue('column', '')
    setValue('value', '')
    if (chat === null) {
      setMessages([
        {
          role: 'assistant',
          content: t('message.notApiKey')
        }
      ])
    } else {
      setMessages([
        {
          role: 'assistant',
          content: t('message.initFillDataMessage')
        }
      ])
    }
  }, [columns])

  useEffect(() => {
    if (column) {
      const columnInfo = columns.find(x => x.field === column)
      if (columnInfo) {
        if (columnInfo.items) {
          setValueType('select')
          setItems(columnInfo.items)
        } else {
          setValueType('text')
          setItems([])
        }
      }
    }
  }, [columns, column])

  const onSubmit = handleSubmit((data) => {
    fillData(data.column, data.value)
  })

  return {
    setOpen,
    open,
    control,
    onSubmit,
    valueType,
    items,
    method,
    applyChat: {
      chat,
      messages,
      skeleton
    }
  }
}

export default useFillData
