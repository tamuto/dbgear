import { create } from 'zustand'

const useLoading = create<LodingState>((set, get) => ({
  loading: null,
  isLoading: () => get().loading !== null,
  setLoading: (target) => set({ loading: target })
}))

export default useLoading
