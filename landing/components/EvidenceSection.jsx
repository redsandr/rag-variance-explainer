import { useEffect, useRef, useState } from 'react';
import { METRICS, CHART_DATA } from '../data/constants';

export default function EvidenceSection() {
  const evidenceRef = useRef(null);
  const [evidenceVisible, setEvidenceVisible] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    function check() { setIsMobile(window.innerWidth < 768); }
    check();
    window.addEventListener('resize', check);
    return () => window.removeEventListener('resize', check);
  }, []);

  useEffect(() => {
    const el = evidenceRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setEvidenceVisible(true);
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
    <section id="evidence" ref={evidenceRef} className="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32">
      <div className="mb-10 sm:mb-14 text-center">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Evidence, not claims</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold mb-4">Accuracy, tested and measured.</p>
        <p className="text-sm sm:text-base max-w-2xl mx-auto" style={{ color: 'var(--text-dim)' }}>
          Tested against 40 real questions with known correct answers, before and after adding a relevance-ranking
          step. The hardest cases went from being missed entirely to found first.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6">
        {METRICS.map((m) => (
          <div key={m.label} className="rounded-2xl p-4 sm:p-5 card">
            <div className="text-2xl sm:text-3xl font-bold tabular mb-1" style={{ color: 'var(--accent)' }}>{m.value}</div>
            <div className="text-xs sm:text-sm font-medium mb-1 leading-tight">{m.label}</div>
            <div className="text-[11px] sm:text-xs" style={{ color: 'var(--text-mute)' }}>{m.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-5 gap-4 sm:gap-6 items-end mb-6 rounded-2xl p-4 sm:p-6 md:p-8 card">
        <div className="md:col-span-3 w-full min-w-0">
          <div className="flex gap-2 sm:gap-3">
            <div className="flex flex-col justify-between h-40 sm:h-48 md:h-56 pb-6 text-[9px] sm:text-[10px] mono shrink-0" style={{ color: 'var(--text-mute)' }}>
              <span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span>
            </div>
            <div className="relative flex-1 min-w-0">
              <div className="absolute inset-0 flex flex-col justify-between pb-6" aria-hidden="true">
                {[0, 1, 2, 3, 4].map((i) => (
                  <div key={i} className="border-t" style={{ borderColor: 'var(--border)' }}></div>
                ))}
              </div>
              <div className="relative grid grid-cols-4 h-40 sm:h-48 md:h-56 items-end" style={{ gap: isMobile ? '4px' : '8px' }}>
                {CHART_DATA.map((d, idx) => (
                  <div key={d.label} className="flex flex-col items-center justify-end h-full gap-1 sm:gap-2">
                    <div className={`flex items-end ${isMobile ? 'justify-center' : 'gap-1 sm:gap-2'} h-28 sm:h-36 md:h-40 w-full justify-center`}>
                      {/* Base bar — hide on mobile to avoid text numpuk */}
                      <div className={`flex-col items-center justify-end h-full ${isMobile ? 'hidden' : 'flex'} sm:flex`}>
                        <span
                          className="text-[9px] sm:text-[10px] mono font-semibold mb-1 leading-none"
                          style={{ color: 'var(--text-mute)', opacity: evidenceVisible ? 1 : 0, transition: `opacity 0.3s ease ${idx * 0.08 + 0.5}s` }}
                        >
                          {Math.round(d.base * 100)}%
                        </span>
                        <div
                          className="w-3 sm:w-4 md:w-6 rounded-t"
                          style={{
                            height: evidenceVisible ? `${d.base * 100}%` : 0,
                            background: 'var(--border-strong)',
                            transition: `height 0.9s cubic-bezier(0.16,1,0.3,1) ${idx * 0.08}s`,
                          }}
                        ></div>
                      </div>
                      <div className="flex flex-col items-center justify-end h-full">
                        <span
                          className="text-[9px] sm:text-[10px] mono font-bold mb-1 leading-none"
                          style={{ color: 'var(--accent)', opacity: evidenceVisible ? 1 : 0, transition: `opacity 0.3s ease ${idx * 0.08 + 0.65}s` }}
                        >
                          {Math.round(d.ce * 100)}%
                        </span>
                        <div
                          className={`${isMobile ? 'w-6' : 'w-3 sm:w-4 md:w-6'} rounded-t`}
                          style={{
                            height: evidenceVisible ? `${d.ce * 100}%` : 0,
                            background: 'var(--accent)',
                            transition: `height 0.9s cubic-bezier(0.16,1,0.3,1) ${idx * 0.08 + 0.15}s`,
                          }}
                        ></div>
                      </div>
                    </div>
                    <div className="text-[9px] sm:text-[10px] mono font-medium" style={{ color: 'var(--text-dim)' }}>{d.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
        <div className="md:col-span-2 space-y-3 sm:space-y-4 md:pl-6 md:border-l" style={{ borderColor: 'var(--border)' }}>
          <div>
            <div className="text-sm font-semibold mb-1">Right source found on the first try</div>
            <div className="text-xs" style={{ color: 'var(--text-mute)' }}>Before vs. after adding a relevance-ranking step</div>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 rounded-sm shrink-0" style={{ background: 'var(--border-strong)' }}></span>
            <span style={{ color: 'var(--text-dim)' }}>Before ranking step</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="h-2.5 w-2.5 rounded-sm shrink-0" style={{ background: 'var(--accent)' }}></span>
            <span style={{ color: 'var(--text-dim)' }}>After ranking step</span>
          </div>
          <div className="pt-3">
            <div className="text-2xl sm:text-3xl font-bold tabular" style={{ color: 'var(--accent)' }}>0.52 &rarr; 0.66</div>
            <div className="text-xs mt-1" style={{ color: 'var(--text-mute)' }}>search score (higher = right answer found sooner)</div>
          </div>
        </div>
      </div>

      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4">
        <div className="rounded-xl p-4 sm:p-5 card card-hover">
          <div className="mono text-[11px] sm:text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Chipotle overhead-cost question</div>
          <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm">
            <span style={{ color: 'var(--text-mute)' }}>was result #17</span>
            <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
            <span className="font-semibold" style={{ color: 'var(--accent)' }}>now #1</span>
          </div>
        </div>
        <div className="rounded-xl p-4 sm:p-5 card card-hover">
          <div className="mono text-[11px] sm:text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Cracker Barrel labor-cost question</div>
          <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm">
            <span style={{ color: 'var(--text-mute)' }}>was result #17</span>
            <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
            <span className="font-semibold" style={{ color: 'var(--accent)' }}>now #1</span>
          </div>
        </div>
        <div className="rounded-xl p-4 sm:p-5 card card-hover">
          <div className="mono text-[11px] sm:text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Questions it used to miss entirely</div>
          <div className="flex items-center gap-2 sm:gap-3 text-xs sm:text-sm">
            <span style={{ color: 'var(--text-mute)' }}>4 of 20</span>
            <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
            <span className="font-semibold" style={{ color: 'var(--accent)' }}>0 of 20</span>
          </div>
        </div>
      </div>
    </section>
  );
}
