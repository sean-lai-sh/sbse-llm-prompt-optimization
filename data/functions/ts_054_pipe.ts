export function pipe<T>(...fns: Array<(x: T) => T>): (x: T) => T {
  return (x: T): T => fns.reduce((acc, fn) => fn(acc), x);
}
