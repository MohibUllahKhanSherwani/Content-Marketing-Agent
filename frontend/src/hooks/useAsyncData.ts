import { useEffect, useState } from 'react'

type AsyncState<T> = {
  data: T | null
  loading: boolean
  error: string | null
}

export function useAsyncData<T>(loader: () => Promise<T>, deps: unknown[] = []) {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const run = () => {
    setState((current) => ({ ...current, loading: true, error: null }))
    loader()
      .then((data) => {
        setState({ data, loading: false, error: null })
      })
      .catch(() => {
        setState({ data: null, loading: false, error: 'Unable to load data.' })
      })
  }

  useEffect(() => {
    let active = true
    loader()
      .then((data) => {
        if (!active) return
        setState({ data, loading: false, error: null })
      })
      .catch(() => {
        if (!active) return
        setState({ data: null, loading: false, error: 'Unable to load data.' })
      })
    return () => {
      active = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return { ...state, reload: run }
}
