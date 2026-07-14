export function pluralWniosek(n: number): string {
  if (n === 1) return 'wniosek'
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14)) return 'wnioski'
  return 'wniosków'
}
