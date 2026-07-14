export function useModalForm<T>(onSuccess: (result: T) => void | Promise<void>) {
  const loading = ref(false)
  const { showToast, reportApiError } = useToast()

  async function submit(action: () => Promise<T>, successStatus = 200) {
    loading.value = true
    try {
      const result = await action()
      showToast(successStatus)
      await onSuccess(result)
    } catch (err: unknown) {
      reportApiError(err)
    } finally {
      loading.value = false
    }
  }

  return { loading, submit }
}
