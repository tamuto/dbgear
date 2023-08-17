interface LodingState {
  loading: object | null,
  isLoading: () => boolean,
  setLoading: (loading: object | null) => void
}
