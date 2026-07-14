export function useModalForm(onSuccess: () => void | Promise<void>) {
  const loading = ref(false)
  const { showToast, reportApiError } = useToast()

  async function submit(action: () => Promise<unknown>, successStatus = 200) {
    loading.value = true
    try {
      await action()
      showToast(successStatus)
      await onSuccess()
    } catch (err: unknown) {
      reportApiError(err)
    } finally {
      loading.value = false
    }
  }

  return { loading, submit }
}
