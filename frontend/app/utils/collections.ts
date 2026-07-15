export function replaceById<T extends { id: number }>(list: T[], row: T): T[] {
  const idx = list.findIndex((item) => item.id === row.id)
  return idx === -1 ? list : [...list.slice(0, idx), row, ...list.slice(idx + 1)]
}
