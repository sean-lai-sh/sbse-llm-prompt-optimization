export default function partitionArray(arr, predicate) {
  const truthy = [];
  const falsy = [];
  for (const item of arr) {
    if (predicate(item)) truthy.push(item);
    else falsy.push(item);
  }
  return [truthy, falsy];
}
