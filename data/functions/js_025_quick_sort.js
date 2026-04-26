export default function quickSort(arr) {
  if (arr.length <= 1) return arr;
  const pivot = arr[Math.floor(arr.length / 2)];
  const left = [];
  const middle = [];
  const right = [];
  for (const el of arr) {
    if (el < pivot) left.push(el);
    else if (el > pivot) right.push(el);
    else middle.push(el);
  }
  return [...quickSort(left), ...middle, ...quickSort(right)];
}
