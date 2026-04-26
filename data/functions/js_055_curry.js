export default function curry(fn) {
  const arity = fn.length;
  return function curried(...args) {
    if (args.length >= arity) {
      return fn.apply(this, args);
    }
    return function (...moreArgs) {
      return curried.apply(this, args.concat(moreArgs));
    };
  };
}
