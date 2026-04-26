export default function validateEmail(email) {
  if (typeof email !== "string") return false;
  const trimmed = email.trim();
  if (trimmed.length === 0 || trimmed.length > 254) return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  if (!emailRegex.test(trimmed)) return false;
  const [local, domain] = trimmed.split("@");
  if (local.length > 64) return false;
  if (domain.startsWith(".") || domain.endsWith(".")) return false;
  return true;
}
