export default function unflattenObject(obj, separator = ".") {
  if (typeof obj !== "object" || obj === null) return {};
  const result = {};
  for (const [flatKey, value] of Object.entries(obj)) {
    const keys = flatKey.split(separator);
    let current = result;
    for (let i = 0; i < keys.length - 1; i++) {
      const k = keys[i];
      if (typeof current[k] !== "object" || current[k] === null) {
        current[k] = {};
      }
      current = current[k];
    }
    current[keys[keys.length - 1]] = value;
  }
  return result;
}
