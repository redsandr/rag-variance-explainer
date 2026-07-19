import { useEffect, useRef, useState } from 'react';

const DEMO_ITEMS = [
  {
    q: "Why did Chipotle's labor costs increase?",
    a: "Labor costs rose mainly from wage inflation and minimum wage increases in states like California, partially offset by sales leverage as comparable restaurant sales grew.",
    tag: 'CMG 10-Q, p. 12',
  },
  {
    q: "What drove Walmart's e-commerce growth?",
    a: "Growth came mainly from higher omnichannel penetration and continued adoption of store-fulfilled pickup and delivery.",
    tag: 'WMT 10-K, p. 28',
  },
  {
    q: "How did Target's gross margin change?",
    a: "Gross margin improved on a favorable shift in merchandise mix, along with lower promotional activity and reduced shrink.",
    tag: 'TGT 10-Q, p. 19',
  },
];

export default function HeroDemoCard() {
  const [activeIdx, setActiveIdx] = useState(0);
  const [typedQ, setTypedQ] = useState('');
  const [showAnswer, setShowAnswer] = useState(false);
  const [answerText, setAnswerText] = useState('');
  const [busy, setBusy] = useState(false);
  const timersRef = useRef([]);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  function startDemo(idx) {
    if (busy) return;
    setBusy(true);
    setActiveIdx(idx);
    setShowAnswer(false);
    setAnswerText('');
    setTypedQ('');

    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];

    const item = DEMO_ITEMS[idx];
    let i = 0;

    function tickQ() {
      if (!mountedRef.current) return;
      if (i <= item.q.length) {
        setTypedQ(item.q.slice(0, i));
        i++;
        setTimeout(tickQ, 28);
      } else {
        const t = setTimeout(() => {
          if (!mountedRef.current) return;
          setShowAnswer(true);
          let j = 0;
          function tickA() {
            if (!mountedRef.current) return;
            if (j <= item.a.length) {
              setAnswerText(item.a.slice(0, j));
              j++;
              setTimeout(tickA, 12);
            } else {
              setBusy(false);
            }
          }
          setTimeout(tickA, 300);
        }, 400);
        timersRef.current.push(t);
      }
    }
    tickQ();
  }

  useEffect(() => {
    const t = setTimeout(() => startDemo(0), 600);
    timersRef.current.push(t);
    return () => { timersRef.current.forEach(clearTimeout); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="mx-auto max-w-2xl w-full relative z-10 mt-10 sm:mt-16 mb-12 sm:mb-20">
      <div
        className="rounded-xl overflow-hidden"
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          boxShadow: '0 8px 40px rgba(0,0,0,0.4)',
        }}
      >
        {/* Terminal header */}
        <div className="flex items-center gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 sm:py-3" style={{ background: 'var(--surface-alt)', borderBottom: '1px solid var(--border)' }}>
          <span className="h-2 w-2.5 sm:h-2.5 sm:w-2.5 rounded-full" style={{ background: 'var(--accent)' }} />
          <span className="h-2 w-2.5 sm:h-2.5 sm:w-2.5 rounded-full" style={{ background: 'var(--accent)' }} />
          <span className="h-2 w-2.5 sm:h-2.5 sm:w-2.5 rounded-full" style={{ background: 'var(--border-strong)' }} />
          <span className="text-[10px] sm:text-[11px] mono ml-1 sm:ml-2" style={{ color: 'var(--text-mute)' }}>variance-explainer — demo</span>
        </div>

        {/* Body */}
        <div className="p-3 sm:p-6">
          {/* Prompt + question */}
          <div className="mono text-xs sm:text-sm leading-relaxed mb-3 sm:mb-4" style={{ color: 'var(--text-dim)' }}>
            <span style={{ color: 'var(--accent)' }}>$</span> ask <span className="text-[10px] sm:text-xs" style={{ color: 'var(--text-mute)' }}>--question</span>
            <div className="mt-1 sm:mt-1.5 text-xs sm:text-sm" style={{ color: 'var(--text)' }}>
              &quot;{typedQ}<span className="cursor-blink">&#9608;</span>&quot;
            </div>
          </div>

          {/* Answer */}
          <div
            className="rounded-lg p-3 sm:p-4 transition-all duration-500"
            style={{
              background: 'var(--accent-soft)',
              borderLeft: '3px solid var(--accent)',
              opacity: showAnswer ? 1 : 0,
              transform: showAnswer ? 'translateY(0)' : 'translateY(8px)',
            }}
          >
            <div className="flex items-center gap-1.5 sm:gap-2 mb-1.5 sm:mb-2 flex-wrap">
              <span
                className="text-[9px] sm:text-[10px] font-bold px-1.5 sm:px-2 py-0.5 rounded"
                style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}
              >
                {DEMO_ITEMS[activeIdx].tag}
              </span>
              <span className="text-[9px] sm:text-[10px] font-semibold px-1.5 sm:px-2 py-0.5 rounded-full score-high">94%</span>
            </div>
            <p className="text-xs sm:text-sm leading-relaxed" style={{ color: 'var(--text-dim)' }}>
              {answerText}<span className="cursor-blink">&#9608;</span>
            </p>
          </div>
        </div>
      </div>

      {/* Question chips */}
      <div className="flex flex-wrap justify-center gap-1.5 sm:gap-2 mt-3 sm:mt-4">
        {DEMO_ITEMS.map((item, idx) => (
          <button
            key={item.q}
            onClick={() => startDemo(idx)}
            disabled={busy}
            className="text-[10px] sm:text-xs px-2 sm:px-3 py-1.5 rounded-lg font-medium transition-all leading-tight"
            style={{
              background: idx === activeIdx ? 'var(--accent-soft)' : 'transparent',
              border: '1px solid',
              borderColor: idx === activeIdx ? 'var(--accent)' : 'var(--border)',
              color: idx === activeIdx ? 'var(--accent-light)' : 'var(--text-mute)',
              opacity: busy ? 0.5 : 1,
              maxWidth: '100%',
            }}
          >
            {item.q.length > 25 ? item.q.slice(0, 22) + '...' : item.q}
          </button>
        ))}
      </div>
    </div>
  );
}
