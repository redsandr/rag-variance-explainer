import { useEffect, useRef, useState } from 'react';

const DEMO_ITEMS = [
  {
    q: "Why did Chipotle's labor costs increase?",
    a: "Labor costs rose mainly from wage inflation and minimum wage increases in states like California, partially offset by sales leverage as comparable restaurant sales grew.",
    tag: 'CMG 10-Q, p. 12',
    score: 94,
  },
  {
    q: "What drove Walmart's e-commerce growth?",
    a: "Growth came mainly from higher omnichannel penetration and continued adoption of store-fulfilled pickup and delivery.",
    tag: 'WMT 10-K, p. 28',
    score: 91,
  },
  {
    q: "How did Target's gross margin change?",
    a: "Gross margin improved on a favorable shift in merchandise mix, along with lower promotional activity and reduced shrink.",
    tag: 'TGT 10-Q, p. 19',
    score: 88,
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
    <section id="demo" className="px-5 sm:px-7 py-24 md:py-28">
      <div className="w-full max-w-[860px] mx-auto">
        <div className="section-head">
          <span className="sec-num">03</span>
          <span className="sec-label">Live demo</span>
          <span className="sec-line"></span>
        </div>

        <div className="term">
          <div className="term-top">
            <span className="term-dot" style={{ background: 'var(--accent)' }}></span>
            <span className="term-dot" style={{ background: 'var(--accent-dark)' }}></span>
            <span className="term-dot" style={{ background: 'var(--border-strong)' }}></span>
            <span className="term-title">variance-explainer - demo</span>
          </div>
          <div className="term-body">
            <div className="mono text-xs sm:text-sm" style={{ color: 'var(--text-dim)' }}>
              <span style={{ color: 'var(--accent)' }}>$</span>&nbsp;ask&nbsp;<span style={{ color: 'var(--text-mute)' }}>--question</span>
              <div className="mt-2.5 text-sm sm:text-[15px]" style={{ color: 'var(--text)' }}>
                &ldquo;{typedQ}<span className="cursor-blink" style={{ color: 'var(--accent)' }}>&#9608;</span>&rdquo;
              </div>
            </div>

            <div
              className="answer-box"
              style={{ opacity: showAnswer ? 1 : 0, transform: showAnswer ? 'translateY(0)' : 'translateY(8px)', transition: 'opacity 0.4s ease, transform 0.4s ease' }}
            >
              <div>
                <div className="answer-tag">
                  {DEMO_ITEMS[activeIdx].tag} &middot; confidence {DEMO_ITEMS[activeIdx].score}%
                </div>
                <p className="mt-1.5 text-sm leading-relaxed" style={{ color: 'var(--text-dim)' }}>
                  {answerText}<span className="cursor-blink" style={{ color: 'var(--accent)' }}>&#9608;</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap justify-center gap-2 mt-5">
          {DEMO_ITEMS.map((item, idx) => (
            <button
              key={item.q}
              onClick={() => startDemo(idx)}
              disabled={busy}
              className={`chip ${idx === activeIdx ? 'chip-on' : ''}`}
              style={{ opacity: busy ? 0.5 : 1, maxWidth: '100%' }}
            >
              {item.q.length > 30 ? item.q.slice(0, 28) + '...' : item.q}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}