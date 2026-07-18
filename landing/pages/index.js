import { useEffect, useRef, useState } from 'react';

const HERO_QUESTION = "Why did Chipotle's labor costs increase?";
const PIPE_QUESTION = "Why did Chipotle's labor costs increase?";

const CHART_DATA = [
  { label: 'Top 1', base: 0.18, ce: 0.23 },
  { label: 'Top 3', base: 0.24, ce: 0.45 },
  { label: 'Top 5', base: 0.33, ce: 0.52 },
  { label: 'Top 10', base: 0.55, ce: 0.7 },
];

const USE_CASES = [
  { q: "Why did Chipotle's labor costs change?", a: 'Wage inflation, CA minimum wage, sales leverage', src: 'CMG 10-K/10-Q' },
  { q: "What drove Walmart's e-commerce growth?", a: 'Omnichannel penetration, store-fulfilled pickup', src: 'WMT 10-K/10-Q' },
  { q: "How did Target's gross margin rate change?", a: 'Merchandise mix, promotions, shrink impact', src: 'TGT 10-K/10-Q' },
  { q: "How did Darden's Chuy's acquisition impact revenue?", a: 'Purchase price, sales contribution, segment profit', src: 'DRI 10-K/10-Q' },
  { q: 'How do WMT and TGT compare on inventory turnover?', a: 'Cross-retail inventory trends, shrink reduction', src: 'WMT + TGT' },
];

const FEATURES = [
  { t: 'Understands plain-language questions', d: "Ask the way you'd ask a colleague. No need to know exact filing terms or section names." },
  { t: 'Cites its sources', d: 'Every answer points back to the exact filing and page, so you can verify it yourself before it goes in a report.' },
  { t: 'Pulls straight from SEC filings', d: 'Automatically fetches the relevant sections from 10-Ks and 10-Qs across 7 companies — no manual PDF searching.' },
  { t: 'Works across industries', d: 'Tested on retail with no drop in accuracy compared to restaurants — not tuned to look good on just one industry.' },
  { t: 'Checked against the source', d: 'Roughly 3 out of 4 answers verified as fully accurate against the original filing text, with ongoing work to improve that further.' },
  { t: 'Flexible on privacy and cost', d: 'Runs fully offline on your own machine, or connects to a cloud AI provider if you prefer — your data, your choice.' },
];

const ROADMAP = [
  'International filings, not just US-based companies',
  'Follow-up questions in the same conversation, not just one-off queries',
  'One-click setup, no command line required',
  'A version tuned specifically on financial language for even higher accuracy',
  'A public demo anyone can try without installing anything',
];

const CODE_SNIPPETS = {
  local: `# Clone & setup
git clone https://github.com/redsandr/rag-variance-explainer
cd rag-variance-explainer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Build index & run
python src/build_index.py
streamlit run app.py`,
  openai: `# Clone & setup
git clone https://github.com/redsandr/rag-variance-explainer
cd rag-variance-explainer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Set in .env:
# LLM_BACKEND=openai
# OPENAI_API_KEY=sk-...

python src/build_index.py
streamlit run app.py`,
  claude: `# Clone & setup
git clone https://github.com/redsandr/rag-variance-explainer
cd rag-variance-explainer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Set in .env:
# LLM_BACKEND=anthropic
# ANTHROPIC_API_KEY=sk-ant-...

python src/build_index.py
streamlit run app.py`,
};

const PIPE_STEPS = [
  { title: 'Understand the question', label: 'sections searched', kind: 'count', to: 740, duration: 700 },
  { title: 'Search the filings', label: 'possible matches', kind: 'count', to: 20, duration: 600 },
  { title: 'Rank by relevance', label: 'best match found', kind: 'score', to: 0.91, duration: 700 },
  { title: 'Write the answer', label: 'sourced answer', kind: 'writing' },
];

function useTypewriter(text, { startDelay = 0, speed = 32, onDone } = [], deps = []) {
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

export default function Home() {
  const [theme, setTheme] = useState('light');
  const [showHeroAnswer, setShowHeroAnswer] = useState(false);
  const [tab, setTab] = useState('local');
  const [copyLabel, setCopyLabel] = useState('Copy');

  // Apply theme to the actual <html> element so CSS selectors
  // like html[data-theme="dark"] in globals.css take effect.
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Pipeline animation state
  const [pipelineKey, setPipelineKey] = useState(0); // bump to restart
  const [activeStep, setActiveStep] = useState(-1);
  const [stepValues, setStepValues] = useState(['—', '—', '—', '—']);
  const [pipeOutputVisible, setPipeOutputVisible] = useState(false);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const howRef = useRef(null);
  const timersRef = useRef([]);

  const heroTyped = useTypewriter(HERO_QUESTION, {
    startDelay: 600,
    speed: 35,
    onDone: () => setTimeout(() => setShowHeroAnswer(true), 400),
  });

  const pipeTyped = useTypewriter(
    PIPE_QUESTION,
    {
      startDelay: 0,
      speed: 28,
      onDone: () => {
        const t = setTimeout(() => setActiveStep(0), 300);
        timersRef.current.push(t);
      },
    },
    [pipelineKey]
  );

  function toggleTheme() {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'));
  }

  // Drive pipeline steps
  useEffect(() => {
    if (activeStep < 0) return;
    if (activeStep >= PIPE_STEPS.length) {
      const t1 = setTimeout(() => setPipeOutputVisible(true), 200);
      const t2 = setTimeout(() => {
        if (pipelineRunning) {
          // restart loop
          setActiveStep(-1);
          setStepValues(['—', '—', '—', '—']);
          setPipeOutputVisible(false);
          setPipelineKey((k) => k + 1);
        }
      }, 3400);
      timersRef.current.push(t1, t2);
      return;
    }

    const step = PIPE_STEPS[activeStep];
    if (step.kind === 'count') {
      animateCount(activeStep, 0, step.to, step.duration);
    } else if (step.kind === 'score') {
      animateCount(activeStep, 0, step.to, step.duration, true);
    } else if (step.kind === 'writing') {
      let dots = 0;
      const interval = setInterval(() => {
        dots = (dots + 1) % 4;
        setStepValues((prev) => {
          const next = [...prev];
          next[activeStep] = 'writing' + '.'.repeat(dots);
          return next;
        });
      }, 200);
      const stopT = setTimeout(() => clearInterval(interval), 650);
      timersRef.current.push(stopT);
    }

    const t = setTimeout(() => setActiveStep((s) => s + 1), 750);
    timersRef.current.push(t);

    return () => {
      // cleanup handled globally on unmount / restart
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeStep, pipelineRunning]);

  function animateCount(idx, from, to, duration, isScore = false) {
    const start = performance.now();
    function frame(now) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      const val = from + (to - from) * eased;
      setStepValues((prev) => {
        const next = [...prev];
        next[idx] = isScore ? val.toFixed(2) : String(Math.round(val));
        return next;
      });
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  // IntersectionObserver to auto-loop pipeline
  useEffect(() => {
    const el = howRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setPipelineRunning(true);
            setActiveStep(-1);
            setStepValues(['—', '—', '—', '—']);
            setPipeOutputVisible(false);
            setPipelineKey((k) => k + 1);
          } else {
            setPipelineRunning(false);
            timersRef.current.forEach(clearTimeout);
            timersRef.current = [];
          }
        });
      },
      { threshold: 0.4 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

  function copyCode() {
    navigator.clipboard.writeText(CODE_SNIPPETS[tab]).then(() => {
      setCopyLabel('Copied');
      setTimeout(() => setCopyLabel('Copy'), 1500);
    });
  }

  return (
    <div className="antialiased bg-mesh min-h-screen">
      {/* HEADER */}
      <header
        className="fixed top-0 left-0 right-0 z-50"
        style={{ background: 'var(--header-bg)', backdropFilter: 'blur(12px)', borderBottom: '1px solid var(--border)' }}
      >
        <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-lg flex items-center justify-center" style={{ background: 'var(--accent)' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                <path d="M12 2 L22 8 L22 16 L12 22 L2 16 L2 8 Z" />
              </svg>
            </div>
            <span className="text-sm font-semibold tracking-tight">RAG Variance Explainer</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm">
            <a href="#how" className="nav-link">How it works</a>
            <a href="#evidence" className="nav-link">Evidence</a>
            <a href="#features" className="nav-link">Features</a>
            <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle dark mode">
              {theme === 'dark' ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="4" />
                  <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
                </svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
                </svg>
              )}
            </button>
            <a href="https://github.com/redsandr/rag-variance-explainer" className="px-4 py-2 rounded-lg text-sm font-medium btn-primary">
              GitHub
            </a>
          </nav>
        </div>
      </header>

      <main>
        {/* HERO */}
        <section className="relative min-h-screen flex items-center px-6 pt-24 pb-16 overflow-hidden">
          <div className="mx-auto max-w-6xl w-full grid md:grid-cols-2 gap-16 items-center relative z-10">
            <div>
              <div
                className="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium mb-6"
                style={{ background: 'var(--accent-soft)', color: 'var(--accent-dark)' }}
              >
                <span className="h-1.5 w-1.5 rounded-full" style={{ background: 'var(--green)' }}></span>
                7 companies &middot; 4 industries &middot; your data stays in-house
              </div>
              <h1 className="text-4xl md:text-5xl font-bold leading-[1.1] tracking-tight mb-5" style={{ color: 'var(--text)' }}>
                Ask why a metric moved.
                <br />
                Get an answer <span style={{ color: 'var(--accent)' }}>sourced from the filing.</span>
              </h1>
              <p className="text-base leading-relaxed mb-8 max-w-md" style={{ color: 'var(--text-dim)' }}>
                Ask a plain-language question about real SEC filings — 10-Ks, 10-Qs, MD&amp;A sections — and get a
                sourced answer in minutes, not hours of digging through pages by hand.
              </p>
              <div className="flex items-center gap-3">
                <a href="https://github.com/redsandr/rag-variance-explainer" className="px-5 py-3 rounded-xl text-sm font-semibold btn-primary">
                  View on GitHub
                </a>
                <a href="#how" className="px-5 py-3 rounded-xl text-sm font-medium btn-secondary">
                  See how it works
                </a>
              </div>

              <div className="flex items-center gap-8 mt-10 pt-8" style={{ borderTop: '1px solid var(--border)' }}>
                <div>
                  <div className="text-2xl font-bold tabular" style={{ color: 'var(--green)' }}>4 hrs &rarr; 3 min</div>
                  <div className="text-xs mt-0.5" style={{ color: 'var(--text-mute)' }}>time per variance question</div>
                </div>
                <div>
                  <div className="text-2xl font-bold tabular" style={{ color: 'var(--accent)' }}>100%</div>
                  <div className="text-xs mt-0.5" style={{ color: 'var(--text-mute)' }}>right answer found, every industry tested</div>
                </div>
                <div>
                  <div className="text-2xl font-bold tabular">74%</div>
                  <div className="text-xs mt-0.5" style={{ color: 'var(--text-mute)' }}>of answers verified against the filing</div>
                </div>
              </div>
            </div>

            <div className="rounded-2xl overflow-hidden card" style={{ boxShadow: '0 30px 70px -20px rgba(111,143,0,0.18)' }}>
              <div className="flex items-center gap-1.5 px-4 py-3" style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface-alt)' }}>
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--border-strong)' }}></span>
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--border-strong)' }}></span>
                <span className="h-2.5 w-2.5 rounded-full" style={{ background: 'var(--border-strong)' }}></span>
                <span className="ml-3 text-xs mono" style={{ color: 'var(--text-mute)' }}>query.stream</span>
              </div>
              <div className="p-5">
                <div className="mono text-sm mb-4" style={{ color: 'var(--text-dim)' }}>
                  <span style={{ color: 'var(--accent)' }}>&gt;</span> {heroTyped}
                  <span className="cursor-blink">&#9608;</span>
                </div>

                {showHeroAnswer && (
                  <div>
                    <div className="rounded-xl p-4 mb-3 fade-up" style={{ background: 'var(--surface-alt)', border: '1px solid var(--border)' }}>
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-semibold">AI Analysis</span>
                        <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full score-high">sourced</span>
                      </div>
                      <p className="text-xs leading-relaxed" style={{ color: 'var(--text-dim)' }}>
                        Labor costs rose primarily due to California minimum wage increases and continued wage
                        inflation, partially offset by sales leverage from higher transaction volume.
                      </p>
                    </div>

                    <div className="text-[11px] font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-mute)' }}>
                      Source passages &middot; 3
                    </div>

                    <div className="space-y-2">
                      <div
                        className="rounded-lg p-3 fade-up"
                        style={{ background: 'var(--surface-alt)', borderLeft: '2px solid var(--accent)', animationDelay: '0.1s' }}
                      >
                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{ background: 'var(--accent-soft)', color: 'var(--accent-dark)' }}>CMG</span>
                          <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: 'var(--accent-soft)', color: 'var(--text-mute)' }}>10-K</span>
                          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full score-high ml-auto">Top match</span>
                        </div>
                        <p className="text-[11px] mono leading-relaxed" style={{ color: 'var(--text-mute)' }}>
                          &quot;...labor costs as a percentage of revenue increased due to wage inflation and minimum wage...&quot;
                        </p>
                      </div>
                      <div
                        className="rounded-lg p-3 fade-up"
                        style={{ background: 'var(--surface-alt)', borderLeft: '2px solid var(--accent)', animationDelay: '0.2s' }}
                      >
                        <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{ background: 'var(--accent-soft)', color: 'var(--accent-dark)' }}>CMG</span>
                          <span className="text-[10px] px-2 py-0.5 rounded" style={{ background: 'var(--accent-soft)', color: 'var(--text-mute)' }}>10-Q</span>
                          <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full score-mid ml-auto">Also relevant</span>
                        </div>
                        <p className="text-[11px] mono leading-relaxed" style={{ color: 'var(--text-mute)' }}>
                          &quot;...partially offset by sales leverage as comparable restaurant sales grew...&quot;
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* PROBLEM */}
        <section className="max-w-4xl mx-auto px-6 py-24 md:py-32">
          <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>The problem</div>
          <p className="text-2xl md:text-3xl font-semibold leading-tight mb-6">
            Financial analysts spend hours reading MD&amp;A sections every quarter.
          </p>
          <p className="text-base leading-relaxed max-w-2xl" style={{ color: 'var(--text-dim)' }}>
            Scanning tables, cross-referencing periods, hunting for the one sentence that explains why a number moved
            — it&apos;s manual, repetitive, and easy to get wrong under deadline pressure. This tool answers those
            questions directly from the filing text, with the source cited every time.
            <span style={{ color: 'var(--text)', fontWeight: 500 }}>
              {' '}It was built and tested to work the same way across four different industries — restaurant,
              retail, healthcare, energy — not just tuned to look good on one company.
            </span>
          </p>
        </section>

        {/* HOW IT WORKS */}
        <section id="how" ref={howRef} className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14 text-center">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>How it works</div>
            <p className="text-3xl md:text-4xl font-bold">Ask. Retrieve. Answer.</p>
          </div>

          <div className="rounded-2xl card p-8 md:p-10">
            <div className="mono text-sm mb-8 text-center" style={{ color: 'var(--text-dim)', minHeight: 24 }}>
              <span style={{ color: 'var(--accent)' }}>&gt;</span> {pipeTyped}
              <span className="cursor-blink">&#9608;</span>
            </div>

            <div className="grid grid-cols-4 gap-2 md:gap-4 mb-8">
              {PIPE_STEPS.map((step, i) => (
                <div key={step.title} className={`pipe-node rounded-xl p-4 text-center ${activeStep >= i ? 'active' : ''}`}>
                  <div className="text-xs font-semibold mb-2">{step.title}</div>
                  <div
                    className="mono text-lg font-bold tabular"
                    style={{ color: i === 2 && activeStep >= 2 ? 'var(--accent)' : activeStep >= 3 && i === 3 ? 'var(--text)' : 'var(--text-mute)' }}
                  >
                    {stepValues[i]}
                  </div>
                  <div className="text-[10px] mt-1" style={{ color: 'var(--text-mute)' }}>{step.label}</div>
                </div>
              ))}
            </div>

            <div className="h-1 rounded-full overflow-hidden mb-8" style={{ background: 'var(--border)' }}>
              <div
                className="h-full rounded-full"
                style={{
                  background: 'var(--accent)',
                  width: `${Math.max(0, Math.min(activeStep + 1, 4)) * 25}%`,
                  transition: 'width 0.4s ease',
                }}
              ></div>
            </div>

            <div
              className="rounded-xl p-4 transition-opacity duration-300"
              style={{
                background: 'var(--green-soft)',
                border: '1px solid var(--border-strong)',
                opacity: pipeOutputVisible ? 1 : 0,
              }}
            >
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-xs font-semibold" style={{ color: 'var(--green)' }}>Sourced answer ready</span>
              </div>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--green)' }}>
                Wage inflation and CA minimum wage increases, offset by sales leverage. Cited: CMG 10-K p.34, 10-Q p.12.
              </p>
            </div>
          </div>
        </section>

        {/* EVIDENCE */}
        <section id="evidence" className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Evidence, not claims</div>
            <p className="text-3xl md:text-4xl font-bold mb-4">Accuracy, tested and measured.</p>
            <p className="text-base max-w-2xl" style={{ color: 'var(--text-dim)' }}>
              Tested against 40 real questions with known correct answers, before and after adding a
              relevance-ranking step. The hardest cases went from being missed entirely to found first.
            </p>
          </div>

          <div className="grid md:grid-cols-5 gap-6 items-end mb-6 rounded-2xl p-8 card">
            <div className="md:col-span-3">
              <div className="flex gap-3">
                <div className="flex flex-col justify-between h-56 pb-6 text-[10px] mono shrink-0" style={{ color: 'var(--text-mute)' }}>
                  <span>100%</span><span>75%</span><span>50%</span><span>25%</span><span>0%</span>
                </div>
                <div className="relative flex-1">
                  <div className="absolute inset-0 flex flex-col justify-between pb-6" aria-hidden="true">
                    {[0, 1, 2, 3, 4].map((i) => (
                      <div key={i} className="border-t" style={{ borderColor: 'var(--border)' }}></div>
                    ))}
                  </div>
                  <div className="relative grid grid-cols-4 gap-6 h-56 items-end">
                    {CHART_DATA.map((d, idx) => (
                      <div key={d.label} className="flex flex-col items-center justify-end h-full gap-2">
                        <div className="flex items-end gap-2 h-40 w-full justify-center">
                          <div className="flex flex-col items-center justify-end h-full">
                            <span className="text-[10px] mono font-semibold mb-1" style={{ color: 'var(--text-mute)' }}>
                              {Math.round(d.base * 100)}%
                            </span>
                            <div
                              className="w-6 rounded-t bar-rise"
                              style={{ height: `${d.base * 100}%`, background: 'var(--border-strong)', animationDelay: `${idx * 0.08}s` }}
                            ></div>
                          </div>
                          <div className="flex flex-col items-center justify-end h-full">
                            <span className="text-[10px] mono font-bold mb-1" style={{ color: 'var(--accent)' }}>
                              {Math.round(d.ce * 100)}%
                            </span>
                            <div
                              className="w-6 rounded-t bar-rise"
                              style={{ height: `${d.ce * 100}%`, background: 'var(--accent)', animationDelay: `${idx * 0.08 + 0.15}s` }}
                            ></div>
                          </div>
                        </div>
                        <div className="text-[10px] mono font-medium" style={{ color: 'var(--text-dim)' }}>{d.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div className="md:col-span-2 space-y-4 md:pl-6 md:border-l" style={{ borderColor: 'var(--border)' }}>
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'var(--border-strong)' }}></span>
                <span style={{ color: 'var(--text-dim)' }}>Before ranking step</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'var(--accent)' }}></span>
                <span style={{ color: 'var(--text-dim)' }}>After ranking step</span>
              </div>
              <div className="pt-3">
                <div className="text-3xl font-bold tabular" style={{ color: 'var(--green)' }}>0.52 &rarr; 0.66</div>
                <div className="text-xs mt-1" style={{ color: 'var(--text-mute)' }}>search score (higher = right answer found sooner)</div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-4">
            <div className="rounded-xl p-5 card card-hover">
              <div className="mono text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Chipotle overhead-cost question</div>
              <div className="flex items-center gap-3 text-sm">
                <span style={{ color: 'var(--text-mute)' }}>was result #17</span>
                <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
                <span className="font-semibold" style={{ color: 'var(--green)' }}>now #1</span>
              </div>
            </div>
            <div className="rounded-xl p-5 card card-hover">
              <div className="mono text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Cracker Barrel labor-cost question</div>
              <div className="flex items-center gap-3 text-sm">
                <span style={{ color: 'var(--text-mute)' }}>was result #17</span>
                <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
                <span className="font-semibold" style={{ color: 'var(--green)' }}>now #1</span>
              </div>
            </div>
            <div className="rounded-xl p-5 card card-hover">
              <div className="mono text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Questions it used to miss entirely</div>
              <div className="flex items-center gap-3 text-sm">
                <span style={{ color: 'var(--text-mute)' }}>4 of 20</span>
                <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
                <span className="font-semibold" style={{ color: 'var(--green)' }}>0 of 20</span>
              </div>
            </div>
          </div>
        </section>

        {/* USE CASES */}
        <section className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Use cases</div>
            <p className="text-3xl md:text-4xl font-bold">Real questions, real answers.</p>
          </div>
          <div className="rounded-2xl overflow-hidden card">
            <table className="w-full text-left text-sm">
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface-alt)' }}>
                  <th className="px-6 py-4 font-medium" style={{ color: 'var(--text-dim)' }}>Question</th>
                  <th className="px-6 py-4 font-medium" style={{ color: 'var(--text-dim)' }}>Answer includes</th>
                  <th className="px-6 py-4 font-medium" style={{ color: 'var(--text-dim)' }}>Source</th>
                </tr>
              </thead>
              <tbody>
                {USE_CASES.map((uc) => (
                  <tr key={uc.q} style={{ borderBottom: '1px solid var(--border)' }} className="hover:brightness-95 transition-all">
                    <td className="px-6 py-4 font-medium">{uc.q}</td>
                    <td className="px-6 py-4" style={{ color: 'var(--text-dim)' }}>{uc.a}</td>
                    <td className="px-6 py-4">
                      <span
                        className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                        style={{ background: 'var(--accent-soft)', color: 'var(--accent-dark)' }}
                      >
                        {uc.src}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* FEATURES */}
        <section id="features" className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Features</div>
            <p className="text-3xl md:text-4xl font-bold">Built for accuracy, security, and trust.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-4">
            {FEATURES.map((f) => (
              <div key={f.t} className="rounded-xl p-6 card card-hover">
                <h3 className="text-sm font-semibold mb-2">{f.t}</h3>
                <p className="text-sm leading-relaxed" style={{ color: 'var(--text-dim)' }}>{f.d}</p>
              </div>
            ))}
          </div>
        </section>

        {/* QUICK START */}
        <section className="max-w-4xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Quick start</div>
            <p className="text-3xl md:text-4xl font-bold">Running in two minutes.</p>
            <p className="text-base mt-3" style={{ color: 'var(--text-dim)' }}>For anyone who wants to run it themselves or review exactly how it works under the hood.</p>
          </div>
          <div className="rounded-2xl overflow-hidden card">
            <div className="flex items-center justify-between" style={{ borderBottom: '1px solid var(--border)' }}>
              <div className="flex">
                {['local', 'openai', 'claude'].map((t) => (
                  <button
                    key={t}
                    className={`tab-btn px-6 py-3 text-sm font-medium ${tab === t ? 'active' : ''}`}
                    style={{ borderBottom: tab === t ? '2px solid var(--accent)' : '2px solid transparent' }}
                    onClick={() => setTab(t)}
                  >
                    {t === 'local' ? 'Local model' : t === 'openai' ? 'OpenAI API' : 'Claude API'}
                  </button>
                ))}
              </div>
              <button
                className="copy-btn flex items-center gap-1.5 mr-4 px-3 py-1.5 rounded-lg text-xs font-medium"
                style={{ border: '1px solid var(--border-strong)', color: 'var(--text-dim)' }}
                onClick={copyCode}
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" />
                  <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                </svg>
                <span>{copyLabel}</span>
              </button>
            </div>
            <pre className="mono text-sm p-6 overflow-x-auto leading-relaxed" style={{ color: 'var(--text-dim)' }}>
              {CODE_SNIPPETS[tab]}
            </pre>
          </div>
        </section>

        {/* ROADMAP */}
        <section className="max-w-4xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Roadmap</div>
            <p className="text-3xl md:text-4xl font-bold">What&apos;s next.</p>
          </div>
          <div className="grid gap-3">
            {ROADMAP.map((item) => (
              <div key={item} className="flex items-center gap-4 px-6 py-4 rounded-xl card card-hover">
                <span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ background: 'var(--accent)' }}></span>
                <span className="text-sm" style={{ color: 'var(--text-dim)' }}>{item}</span>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer style={{ borderTop: '1px solid var(--border)' }}>
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm" style={{ color: 'var(--text-mute)' }}>
            <span>MIT License</span><span>&middot;</span><span>2026</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <a href="https://github.com/redsandr/rag-variance-explainer" className="nav-link">GitHub</a>
            <a href="https://github.com/redsandr/rag-variance-explainer/tree/master/docs" className="nav-link">Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}