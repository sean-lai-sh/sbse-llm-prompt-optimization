export default function caesarCipher(str, shift) {
  const s = ((shift % 26) + 26) % 26;
  return str.replace(/[a-zA-Z]/g, char => {
    const base = char >= 'a' ? 97 : 65;
    return String.fromCharCode(((char.charCodeAt(0) - base + s) % 26) + base);
  });
}
