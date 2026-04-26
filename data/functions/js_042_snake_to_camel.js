export default function snakeToCamel(str) {
  return str
    .toLowerCase()
    .replace(/_([a-z])/g, (_, char) => char.toUpperCase());
}
