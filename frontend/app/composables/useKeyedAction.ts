export function useKeyedAction<T>(onSuccess: (result: T) => void) {
  const loadingIds = ref<number[]>([])
  const { showToast, reportApiError } = useToast()

  function isLoading(id: number): boolean {
    return loadingIds.value.includes(id)
  }

  async function run(id: number, action: () => Promise<T>) {
    loadingIds.value = [...loadingIds.value, id]
    try {
      const result = await action()
      showToast(200)
      onSuccess(result)
    } catch (err: unknown) {
      reportApiError(err)
    } finally {
      loadingIds.value = loadingIds.value.filter((x) => x !== id)
    }
  }

  return { isLoading, run }
}
