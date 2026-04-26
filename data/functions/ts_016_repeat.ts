export function repeat(s: string, times: number): string {
  return s.repeat(Math.max(0, Math.floor(times)));
}
