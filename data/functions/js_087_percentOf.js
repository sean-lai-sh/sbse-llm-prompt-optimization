export default function percentOf(part, total) {
  if (total === 0) return 0;
  return (part / total) * 100;
}
