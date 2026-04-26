export default function shellSort(arr) {
  const a = [...arr];
  let gap = Math.floor(a.length / 2);

  while (gap > 0) {
    for (let i = gap; i < a.length; i++) {
      const temp = a[i];
      let j = i;
      while (j >= gap && a[j - gap] > temp) {
        a[j] = a[j - gap];
        j -= gap;
      }
      a[j] = temp;
    }
    gap = Math.floor(gap / 2);
  }
  return a;
}
