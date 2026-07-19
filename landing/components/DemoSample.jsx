import { useEffect, useRef, useState } from 'react';
import Vernie from './Vernie';
import { DEMO_ANALYSES } from '../data/constants';

export default function DemoSample() {
  const mountedRef = useRef(true);
  const [activeDemoId, setActiveDemoId] = useState(DEMO_ANALYSES[0].id);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoRevealed, setDemoRevealed] = useState(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  function runDemo(id) {
    if (id === activeDemoId && demoRevealed) return;
    setActiveDemoId(id);
    setDemoRevealed(false);
    setDemoLoading(true);
    setTimeout(() => {
      if (!mountedRef.current) return;
      setDemoLoading(false);
      setDemoRevealed(true);
    }, 550);
  }

  const activeDemo = DEMO_ANALYSES.find((d) => d.id === activeDemoId) || DEMO_ANALYSES[0];

  return (
    <section id="demo" className="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32">
      <div className="mb-10 sm:mb-14 text-center">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Try it</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold mb-4">Pick a question. See the answer.</p>
        <p className="text-sm sm:text-base max-w-xl mx-auto" style={{ color: 'var(--text-dim)' }}>
          Sample output from real questions the tool was tested on — no install required.
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-2 mb-8">
        {DEMO_ANALYSES.map((d) => (
          <button
            key={d.id}
            onClick={() => runDemo(d.id)}
            className="px-3 sm:px-4 py-2 rounded-xl text-[11px] sm:text-sm font-medium text-left leading-tight"
            style={
              d.id === activeDemoId
                ? { background: 'var(--accent)', color: 'var(--btn-text-on-accent)' }
                : { background: 'var(--surface)', border: '1px solid var(--border-strong)', color: 'var(--text)' }
            }
          >
            {d.question}
          </button>
        ))}
      </div>

      <div className="rounded-2xl card p-5 sm:p-6 md:p-8 max-w-2xl mx-auto">
        {demoLoading ? (
          <div className="flex flex-col items-center gap-3 py-10 justify-center" style={{ color: 'var(--text-mute)' }}>
            <Vernie pose="searching" size={48} />
            <div className="flex items-center gap-2">
              <span className="mono text-sm">Analyzing filing</span>
              <span className="cursor-blink mono text-sm">&#9608;</span>
            </div>
          </div>
        ) : (
          <div className="fade-up" key={activeDemo.id}>
            <div className="flex items-center gap-2 mb-1.5 flex-wrap">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}>{activeDemo.ticker}</span>
              <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: 'var(--accent-soft)', color: 'var(--text-mute)' }}>{activeDemo.form}</span>
              <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full score-high ml-auto">{activeDemo.confidence}% confidence</span>
            </div>
            <p className="text-sm font-semibold mb-4">{activeDemo.question}</p>

            <div className="rounded-xl p-4 mb-4" style={{ background: 'var(--surface-alt)', border: '1px solid var(--border)' }}>
              <div className="text-xs font-semibold mb-1.5">Answer</div>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--text-dim)' }}>{activeDemo.answer}</p>
            </div>

            <div className="rounded-xl p-4" style={{ background: 'var(--surface-alt)', borderLeft: '2px solid var(--accent)' }}>
              <div className="text-[11px] font-semibold uppercase tracking-wider mb-1.5" style={{ color: 'var(--text-mute)' }}>
                Cited from {activeDemo.citation}
              </div>
              <p className="text-xs mono leading-relaxed" style={{ color: 'var(--text-mute)' }}>{activeDemo.evidence}</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
