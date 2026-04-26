export default function jsonToCsv(records, delimiter = ",") {
  if (!Array.isArray(records) || records.length === 0) return "";
  const headers = [...new Set(records.flatMap((r) => Object.keys(r)))];
  const escapeField = (val) => {
    const str = val === null || val === undefined ? "" : String(val);
    if (str.includes(delimiter) || str.includes('"') || str.includes("\n")) {
      return `"${str.replace(/"/g, '""')}"`;
    }
    return str;
  };
  const headerRow = headers.map(escapeField).join(delimiter);
  const dataRows = records.map((r) =>
    headers.map((h) => escapeField(r[h])).join(delimiter)
  );
  return [headerRow, ...dataRows].join("\n");
}
