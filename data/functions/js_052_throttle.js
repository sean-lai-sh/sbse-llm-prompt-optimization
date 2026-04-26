export default function throttle(fn, limit) {
  let lastCall = 0;
  let timerId = null;
  return function throttled(...args) {
    const now = Date.now();
    const remaining = limit - (now - lastCall);
    if (remaining <= 0) {
      if (timerId) {
        clearTimeout(timerId);
        timerId = null;
      }
      lastCall = now;
      fn.apply(this, args);
    } else if (!timerId) {
      timerId = setTimeout(() => {
        lastCall = Date.now();
        timerId = null;
        fn.apply(this, args);
      }, remaining);
    }
  };
}
