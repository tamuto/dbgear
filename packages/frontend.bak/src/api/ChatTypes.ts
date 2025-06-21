type Message = {
  role: 'user' | 'assistant' | 'system' | 'skeleton',
  content: string
}

type Choices = {
  finish_reason: string,
  index: number,
  message: {
    role: 'user' | 'assistant' | 'system' | 'skeleton',
    content: string | null,
    function_call?: {
      name: string,
      arguments: string
    }
  }
}
