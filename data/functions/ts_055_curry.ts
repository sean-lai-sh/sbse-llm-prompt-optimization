type CurriedFn<A, B, R> = (a: A) => (b: B) => R;

export function curry<A, B, R>(fn: (a: A, b: B) => R): CurriedFn<A, B, R> {
  return (a: A) => (b: B): R => fn(a, b);
}
