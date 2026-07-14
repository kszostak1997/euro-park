export interface ToastItem {
  id: number
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

let nextToastId = 0

export function useToast() {
  const toasts = useState<ToastItem[]>('toast-items', () => [])

  function dismissToast(id: number) {
    toasts.value = toasts.value.filter((toast) => toast.id !== id)
  }

  function showToast(status: number, message?: string) {
    const toast: ToastItem = {
      id: ++nextToastId,
      status,
      message: message ?? DEFAULT_MESSAGES[status] ?? 'Nieznany błąd',
    }
    toasts.value = [...toasts.value, toast]
    setTimeout(() => dismissToast(toast.id), 5000)
  }

  function reportApiError(err: unknown, fallbackStatus = 500, fallbackMessage?: string): string {
    const fetchError = err as { data?: { detail?: string }; status?: number }
    const status = fetchError.status ?? fallbackStatus
    const message = fetchError.data?.detail ?? fallbackMessage
    showToast(status, message)
    return message ?? DEFAULT_MESSAGES[status] ?? 'Nieznany błąd'
  }

  return { toasts, showToast, dismissToast, reportApiError }
}
