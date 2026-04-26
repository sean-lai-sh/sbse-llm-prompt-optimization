export default function csvToJson(csv, delimiter = ",") {
  if (typeof csv !== "string" || csv.trim().length === 0) return [];
  const lines = csv.trim().split("\n").map((l) => l.trimEnd());
  if (lines.length < 2) return [];
  const parseLine = (line) => {
    const fields = [];
    let current = "";
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i + 1] === '"') { current += '"'; i++; }
        else inQuotes = !inQuotes;
      } else if (ch === delimiter && !inQuotes) {
        fields.push(current); current = "";
      } else {
        current += ch;
      }
    }
    fields.push(current);
    return fields;
  };
  const headers = parseLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseLine(line);
    const obj = {};
    headers.forEach((h, i) => { obj[h] = values[i] !== undefined ? values[i] : ""; });
    return obj;
  });
}
