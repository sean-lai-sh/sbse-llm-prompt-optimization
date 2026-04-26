export default function safeGet(obj, path, defaultValue = undefined) {
  if (obj == null || typeof path !== "string") return defaultValue;
  const keys = path.split(".");
  let current = obj;
  for (const key of keys) {
    if (current == null || typeof current !== "object") return defaultValue;
    current = current[key];
  }
  return current === undefined ? defaultValue : current;
}
