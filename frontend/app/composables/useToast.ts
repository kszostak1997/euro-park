export interface ToastItem {
  id: string
  status: number
  message: string
}

const DEFAULT_MESSAGES: Record<number, string> = {
  200: 'Akcja zakończona pomyślnie',
  201: 'Akcja zakończona pomyślnie',
  400: 'Nieprawidłowe dane',
  401: 'Nie jesteś zalogowany',
  403: 'Brak dostępu',
  404: 'Nie znaleziono',
  409: 'Konflikt danych',
  422: 'Niepoprawne dane',
  429: 'Za dużo zapytań, spróbuj później',
  500: 'Błąd serwera',
}

function formatValidationDetail(detail: unknown): string | undefined {
  if (!Array.isArray(detail)) return undefined
  const messages = detail
    .map((item) => {
      const msg = (item as { msg?: unknown } | null)?.msg
      return typeof msg === 'string' ? msg : undefined
    })
    .filter((msg): msg is string => !!msg)
  return messages.length ? messages.join(', ') : undefined
}

export function useToast() {
  const toasts = useState<ToastItem[]>('toast-items', () => [])

  function dismissToast(id: string) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  function showToast(status: number, message?: string) {
    const toast: ToastItem = {
      id: crypto.randomUUID(),
      status,
      message: message ?? DEFAULT_MESSAGES[status] ?? 'Nieznany błąd',
    }
    toasts.value = [...toasts.value, toast]
    setTimeout(() => dismissToast(toast.id), 5000)
  }

  function extractApiErrorMessage(
    err: unknown,
    fallbackStatus = 500,
    fallbackMessage?: string,
  ): string {
    const fetchError = err as { data?: { detail?: unknown }; status?: number }
    const status = fetchError.status ?? fallbackStatus
    const detail = fetchError.data?.detail
    const message =
      (typeof detail === 'string' ? detail : formatValidationDetail(detail)) ??
      fallbackMessage
    return message ?? DEFAULT_MESSAGES[status] ?? 'Nieznany błąd'
  }

  function reportApiError(
    err: unknown,
    fallbackStatus = 500,
    fallbackMessage?: string,
  ): string {
    const fetchError = err as { status?: number }
    const status = fetchError.status ?? fallbackStatus
    const message = extractApiErrorMessage(err, fallbackStatus, fallbackMessage)
    showToast(status, message)
    return message
  }

  return { toasts, showToast, dismissToast, reportApiError, extractApiErrorMessage }
}
