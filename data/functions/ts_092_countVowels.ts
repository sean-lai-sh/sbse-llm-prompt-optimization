export function countVowels(s: string): number {
  return (s.match(/[aeiouAEIOU]/g) ?? []).length;
}
