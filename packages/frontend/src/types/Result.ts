
interface Result<T> {
  status: string,
  message: string | null,
  data: T,
}

type Callback<T> = (result: T) => void
