export function pluralizePl(
  count: number,
  forms: [one: string, few: string, many: string],
): string {
  if (count === 1) return forms[0]
  const mod10 = count % 10
  const mod100 = count % 100
  return mod10 >= 2 && mod10 <= 4 && !(mod100 >= 12 && mod100 <= 14)
    ? forms[1]
    : forms[2]
}
