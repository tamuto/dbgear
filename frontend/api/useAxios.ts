import axios, { AxiosResponse, AxiosError } from 'axios'
import { enqueueSnackbar } from 'notistack'

import useLoading from '~/api/useLoading'

const useAxios = () => {
  const _resetLoading = () => {
    const isLoading = useLoading.getState().isLoading()
    isLoading && useLoading.getState().setLoading(null)
  }

  const _catchFunc = (error: AxiosError) => {
    enqueueSnackbar(error.message, { variant: 'error' })
  }

  const stub = <T>(url: string, params: object | null = null) => {
    const _thenFunc = (cb: Callback<T>, result: AxiosResponse<Result<T>>) => {
      _resetLoading()
      if (result.data.status === 'OK') {
        cb(result.data.data)
      } else {
        enqueueSnackbar(result.data.message, { variant: 'error' })
      }
    }
    const get = (cb: Callback<T>) => {
      return axios.get(url, { params })
        .then(result => _thenFunc(cb, result))
        .catch(_catchFunc)
    }
    const post = (data: object, cb: Callback<T>) => {
      return axios.post(url, data, { params })
        .then(result => _thenFunc(cb, result))
        .catch(_catchFunc)
    }
    const put = (data: object, cb: Callback<T>) => {
      return axios.put(url, data, { params })
        .then(result => _thenFunc(cb, result))
        .catch(_catchFunc)
    }
    return {
      get,
      post,
      put
    }
  }

  return stub
}

export default useAxios
