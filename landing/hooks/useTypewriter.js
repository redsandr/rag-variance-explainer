import { useEffect, useState } from 'react';

export default function useTypewriter(text, { startDelay = 0, speed = 32, onDone } = [], deps = []) {
  const [typed, setTyped] = useState('');
  useEffect(() => {
    let i = 0;
    let cancelled = false;
    setTyped('');
    const start = setTimeout(function tick() {
      if (cancelled) return;
      if (i <= text.length) {
        setTyped(text.slice(0, i));
        i++;
        setTimeout(tick, speed);
      } else if (onDone) {
        onDone();
      }
    }, startDelay);
    return () => {
      cancelled = true;
      clearTimeout(start);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return typed;
}
