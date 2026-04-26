export default function pivotTable(records, rowKey, colKey, valueKey, aggregator = "sum") {
  const rowValues = [...new Set(records.map((r) => r[rowKey]))];
  const colValues = [...new Set(records.map((r) => r[colKey]))];
  const buckets = {};
  for (const r of records) {
    const rk = r[rowKey];
    const ck = r[colKey];
    const key = `${rk}__${ck}`;
    if (!buckets[key]) buckets[key] = [];
    buckets[key].push(r[valueKey]);
  }
  const agg = (vals) => {
    if (!vals || vals.length === 0) return 0;
    if (aggregator === "sum") return vals.reduce((a, b) => a + b, 0);
    if (aggregator === "avg") return vals.reduce((a, b) => a + b, 0) / vals.length;
    if (aggregator === "count") return vals.length;
    if (aggregator === "min") return Math.min(...vals);
    if (aggregator === "max") return Math.max(...vals);
    return vals.reduce((a, b) => a + b, 0);
  };
  return rowValues.map((rv) => {
    const row = { [rowKey]: rv };
    for (const cv of colValues) {
      row[cv] = agg(buckets[`${rv}__${cv}`]);
    }
    return row;
  });
}
