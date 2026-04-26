export default function groupAndCount(arr, key) {
  if (!Array.isArray(arr)) return {};
  const result = {};
  for (const item of arr) {
    const groupKey = typeof key === "function" ? key(item) : item[key];
    const strKey = String(groupKey);
    if (!result[strKey]) result[strKey] = { items: [], count: 0 };
    result[strKey].items.push(item);
    result[strKey].count++;
  }
  return result;
}
