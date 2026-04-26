export default function mergeDeep(target, ...sources) {
  if (!sources.length) return target;
  const source = sources.shift();
  if (
    typeof target === "object" && target !== null &&
    typeof source === "object" && source !== null &&
    !Array.isArray(target) && !Array.isArray(source)
  ) {
    for (const key of Object.keys(source)) {
      if (
        typeof source[key] === "object" && source[key] !== null &&
        !Array.isArray(source[key])
      ) {
        if (!target[key]) Object.assign(target, { [key]: {} });
        mergeDeep(target[key], source[key]);
      } else {
        Object.assign(target, { [key]: source[key] });
      }
    }
  }
  return mergeDeep(target, ...sources);
}
