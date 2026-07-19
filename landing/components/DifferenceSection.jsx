import { useEffect, useRef, useState } from 'react';
import { DEMO_ANALYSES } from '../data/constants';

export default function DifferenceSection() {
  const diffRef = useRef(null);
  const [diffVisible, setDiffVisible] = useState(false);

  useEffect(() => {
    const el = diffRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setDiffVisible(true);
            obs.disconnect();
          }
        });
      },
      { threshold: 0.35 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  return (
    <section id="difference" ref={diffRef} className="max-w-6xl mx-auto px-4 sm:px-6 pb-20 sm:pb-24 md:pb-32">
      <div className="mb-10 sm:mb-14 text-center">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>The difference</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold">Typical RAG vs. this pipeline.</p>
      </div>
      <div className="relative grid md:grid-cols-2 gap-5">
        <div
          className="hidden md:flex absolute z-20 items-center justify-center rounded-full font-bold text-xs mono"
          style={{
            top: '50%',
            left: '50%',
            width: 52,
            height: 52,
            transform: diffVisible ? 'translate(-50%, -50%) scale(1)' : 'translate(-50%, -50%) scale(0.4)',
            opacity: diffVisible ? 1 : 0,
            transition: 'opacity 0.4s ease 0.5s, transform 0.4s cubic-bezier(0.34,1.56,0.64,1) 0.5s',
            background: 'var(--accent)',
            color: 'var(--btn-text-on-accent)',
            boxShadow: '0 0 0 6px var(--bg), 0 0 24px rgba(212,175,55,0.5)',
          }}
        >
          VS
        </div>

        <div
          className="rounded-2xl p-5 sm:p-6 md:p-8"
          style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            opacity: diffVisible ? 0.68 : 0,
            transform: diffVisible ? 'translateX(0)' : 'translateX(-48px)',
            transition: 'transform 0.7s cubic-bezier(0.16,1,0.3,1), opacity 0.7s ease',
          }}
        >
          <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--text-mute)' }}>Typical RAG</div>
          <p
            className="text-sm leading-relaxed mb-5"
            style={{ color: 'var(--text-dim)', filter: 'blur(0.4px)' }}
          >
            &quot;Labor costs increased due to various operational factors during the period.&quot;
          </p>
          <div className="flex items-center gap-2 text-xs font-medium" style={{ color: 'var(--text-mute)' }}>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <path d="M15 9l-6 6M9 9l6 6" />
            </svg>
            No source. No confidence.
          </div>
        </div>

        <div
          className="rounded-2xl p-5 sm:p-6 md:p-8 card-hover"
          style={{
            background: 'var(--surface)',
            border: '1.5px solid var(--accent)',
            boxShadow: diffVisible ? '0 0 50px -12px rgba(212,175,55,0.4)' : 'none',
            opacity: diffVisible ? 1 : 0,
            transform: diffVisible ? 'translateX(0)' : 'translateX(48px)',
            transition: 'transform 0.7s cubic-bezier(0.16,1,0.3,1) 0.15s, opacity 0.7s ease 0.15s, box-shadow 0.7s ease 0.15s',
          }}
        >
          <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Our approach</div>
          <p className="text-sm leading-relaxed mb-5" style={{ color: 'var(--text)' }}>
            {DEMO_ANALYSES[0].answer}
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <span
              className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold mono"
              style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)', border: '1px solid var(--border-strong)' }}
            >
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <path d="M14 2v6h6" />
              </svg>
              {DEMO_ANALYSES[0].citation}
            </span>
            <span
              className="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold mono score-high"
            >
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <path d="M5 13l4 4L19 7" />
              </svg>
              {DEMO_ANALYSES[0].confidence}%
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
