export function useDisclosure<T = true>() {
  const target = ref<T | null>(null)

  function open(value: T = true as T) {
    target.value = value
  }

  function close() {
    target.value = null
  }

  return { target, open, close }
}
