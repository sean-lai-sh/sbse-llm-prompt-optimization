export default function mapValues(obj, fn) {
  const out = {};
  for (const key of Object.keys(obj)) {
    out[key] = fn(obj[key], key);
  }
  return out;
}
