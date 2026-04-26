export function jsonToCsv(data: Record<string, unknown>[]): string {
  if (data.length === 0) return "";
  const headers = Object.keys(data[0]);
  const escape = (val: unknown): string => {
    const str = String(val ?? "");
    return str.includes(",") || str.includes('"') || str.includes("\n")
      ? `"${str.replace(/"/g, '""')}"`
      : str;
  };
  const rows = data.map((row) => headers.map((h) => escape(row[h])).join(","));
  return [headers.join(","), ...rows].join("\n");
}
