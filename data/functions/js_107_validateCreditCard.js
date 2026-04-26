export default function validateCreditCard(cardNumber) {
  if (typeof cardNumber !== "string") return false;
  const digits = cardNumber.replace(/[\s-]/g, "");
  if (!/^\d{13,19}$/.test(digits)) return false;
  // Luhn algorithm
  let sum = 0;
  let shouldDouble = false;
  for (let i = digits.length - 1; i >= 0; i--) {
    let d = parseInt(digits[i], 10);
    if (shouldDouble) {
      d *= 2;
      if (d > 9) d -= 9;
    }
    sum += d;
    shouldDouble = !shouldDouble;
  }
  return sum % 10 === 0;
}
