import { useEffect, useRef, useState } from 'react';
import Vernie from '../components/Vernie';
import HeroIllustration from '../components/HeroIllustration';

const PIPE_QUESTION = "Why did Chipotle's labor costs increase?";

const HERO_STATS = [
  { to: 3, label: 'minutes per question, down from ~4 hrs', format: (v) => `${Math.round(v)} min` },
  { to: 52, label: 'right source in top-5, up from 33%', format: (v) => `${Math.round(v)}%` },
  { to: 74, label: 'answers verified against the filing', format: (v) => `${Math.round(v)}%` },
  { to: 7, label: 'companies covered, 4 industries', format: (v) => `${Math.round(v)}` },
];

const TRUST_ITEMS = [
  'Grounded in real SEC filings',
  'Every answer cited to a page',
  'Tested across 4 industries',
  'Open source, MIT licensed',
];

const DEMO_ANALYSES = [
  {
    id: 'cmg-labor',
    question: "Why did Chipotle's labor costs increase?",
    ticker: 'CMG',
    form: '10-Q',
    citation: 'CMG 10-Q, p. 12',
    evidence:
      '"...labor costs as a percentage of revenue increased due to wage inflation and minimum wage increases, partially offset by sales leverage as comparable restaurant sales grew..."',
    answer:
      "Labor costs rose mainly from wage inflation and minimum wage increases in states like California, partially offset by sales leverage as comparable restaurant sales grew.",
    confidence: 94,
  },
  {
    id: 'wmt-ecom',
    question: "What drove Walmart's e-commerce growth?",
    ticker: 'WMT',
    form: '10-K',
    citation: 'WMT 10-K, p. 28',
    evidence:
      '"...e-commerce growth was driven by increased omnichannel penetration and continued adoption of store-fulfilled pickup and delivery..."',
    answer:
      "Growth came mainly from higher omnichannel penetration and continued adoption of store-fulfilled pickup and delivery.",
    confidence: 91,
  },
  {
    id: 'tgt-margin',
    question: "How did Target's gross margin change?",
    ticker: 'TGT',
    form: '10-Q',
    citation: 'TGT 10-Q, p. 19',
    evidence:
      '"...gross margin rate increased, reflecting a favorable shift in merchandise mix and lower promotional and shrink-related costs..."',
    answer:
      "Gross margin improved on a favorable shift in merchandise mix, along with lower promotional activity and reduced shrink.",
    confidence: 88,
  },
  {
    id: 'dri-acq',
    question: "How did the Chuy's acquisition affect Darden's revenue?",
    ticker: 'DRI',
    form: '10-K',
    citation: 'DRI 10-K, p. 41',
    evidence:
      '"...the increase in total revenue was driven in part by the acquisition of Chuy\'s, which contributed segment sales beginning in the fiscal third quarter..."',
    answer:
      "The Chuy's acquisition added incremental segment revenue starting in fiscal Q3, contributing to the total revenue increase for the period.",
    confidence: 90,
  },
];

const CHART_DATA = [
  { label: 'Top 1', base: 0.18, ce: 0.23 },
  { label: 'Top 3', base: 0.24, ce: 0.45 },
  { label: 'Top 5', base: 0.33, ce: 0.52 },
  { label: 'Top 10', base: 0.55, ce: 0.7 },
];

const METRICS = [
  { value: '7', label: 'companies covered', sub: '4 industries' },
  { value: '52%', label: 'right source found first try', sub: 'top-5, up from 33%' },
  { value: '74%', label: 'answers fully verified', sub: 'restaurant filings' },
  { value: '3 min', label: 'per variance question', sub: 'down from ~4 hours' },
];

const USE_CASES = [
  { q: "Why did Chipotle's labor costs change?", a: 'Wage inflation, CA minimum wage, sales leverage', src: 'CMG 10-K/10-Q' },
  { q: "What drove Walmart's e-commerce growth?", a: 'Omnichannel penetration, store-fulfilled pickup', src: 'WMT 10-K/10-Q' },
  { q: "How did Target's gross margin rate change?", a: 'Merchandise mix, promotions, shrink impact', src: 'TGT 10-K/10-Q' },
  { q: "How did Darden's Chuy's acquisition impact revenue?", a: 'Purchase price, sales contribution, segment profit', src: 'DRI 10-K/10-Q' },
  { q: 'How do WMT and TGT compare on inventory turnover?', a: 'Cross-retail inventory trends, shrink reduction', src: 'WMT + TGT' },
];

const FEATURES = [
  { t: 'Ask like you would a colleague', d: "No filing jargon required. Ask in plain English and get an answer scoped to what you actually meant." },
  { t: 'Every claim cited to a page', d: 'Each answer points back to the exact filing and page, so you can verify it before it goes in a report.' },
  { t: 'Pulls directly from SEC filings', d: 'Reads straight from 10-Ks and 10-Qs across 7 companies — no manual searching through PDFs.' },
  { t: 'Works across sectors, not just one', d: 'Tested on restaurant, retail, healthcare, and energy filings, with no drop in accuracy between them.' },
  { t: 'Checked against the source', d: "Roughly 3 in 4 answers verified as fully accurate against the original filing text, with ongoing work to push that higher." },
  { t: 'Your filings stay yours', d: 'Runs fully offline on your own machine, or connects to a cloud provider if you prefer — your data, your choice.' },
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
  { title: 'Understand the question', label: 'sections searched', kind: 'count', to: 740, duration: 700, icon: 'search' },
  { title: 'Search the filings', label: 'possible matches', kind: 'count', to: 20, duration: 600, icon: 'filing' },
  { title: 'Rank by relevance', label: 'best match found', kind: 'score', to: 0.91, duration: 700, icon: 'rank' },
  { title: 'Write the answer', label: 'sourced answer', kind: 'writing', icon: 'pen' },
];

const PIPE_ICONS = {
  search: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.3-4.3" />
    </svg>
  ),
  filing: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M9 13h6M9 17h6" />
    </svg>
  ),
  rank: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M6 20V10M12 20V4M18 20v-7" />
    </svg>
  ),
  pen: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 013 3L7 19l-4 1 1-4z" />
    </svg>
  ),
};

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
  const [tab, setTab] = useState('local');
  const [copyLabel, setCopyLabel] = useState('Copy');

  // Sample-analysis demo state
  const [activeDemoId, setActiveDemoId] = useState(DEMO_ANALYSES[0].id);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoRevealed, setDemoRevealed] = useState(true);

  // Pipeline animation state
  const [pipelineKey, setPipelineKey] = useState(0); // bump to restart
  const [activeStep, setActiveStep] = useState(-1);
  const [stepValues, setStepValues] = useState(['—', '—', '—', '—']);
  const [pipeOutputVisible, setPipeOutputVisible] = useState(false);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const howRef = useRef(null);
  const timersRef = useRef([]);
  const diffRef = useRef(null);
  const [diffVisible, setDiffVisible] = useState(false);
  const statsRef = useRef(null);
  const [statValues, setStatValues] = useState(HERO_STATS.map(() => 0));
  const statsAnimatedRef = useRef(false);

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

  function runDemo(id) {
    if (id === activeDemoId && demoRevealed) return;
    setActiveDemoId(id);
    setDemoRevealed(false);
    setDemoLoading(true);
    setTimeout(() => {
      setDemoLoading(false);
      setDemoRevealed(true);
    }, 550);
  }

  const activeDemo = DEMO_ANALYSES.find((d) => d.id === activeDemoId) || DEMO_ANALYSES[0];

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

  // Trigger "The Difference" slide-in once, the first time it scrolls into view
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

  // Count up the hero stats once, the first time they scroll into view
  useEffect(() => {
    const el = statsRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !statsAnimatedRef.current) {
            statsAnimatedRef.current = true;
            const start = performance.now();
            const duration = 1200;
            function frame(now) {
              const t = Math.min(1, (now - start) / duration);
              const eased = 1 - Math.pow(1 - t, 3);
              setStatValues(HERO_STATS.map((s) => s.to * eased));
              if (t < 1) requestAnimationFrame(frame);
            }
            requestAnimationFrame(frame);
          }
        });
      },
      { threshold: 0.5 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, []);

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
            <span className="text-sm font-semibold tracking-tight serif">Variance Explainer</span>
          </div>
          <div className="flex items-center gap-3">
            <Vernie pose="idle" size={28} />
            <nav className="hidden md:flex items-center gap-8 text-sm">
              <a href="#demo" className="nav-link">Sample analysis</a>
              <a href="#how" className="nav-link">How it works</a>
              <a href="#evidence" className="nav-link">Evidence</a>
              <a href="https://github.com/redsandr/rag-variance-explainer" className="px-4 py-2 rounded-lg text-sm font-medium btn-primary">
                GitHub
              </a>
            </nav>
          </div>
        </div>
      </header>

      <main>
        {/* HERO */}
        <section className="relative flex items-center px-6 pt-32 pb-20 overflow-hidden">
          <div className="mx-auto max-w-4xl w-full relative z-10 text-center">
            <div className="flex items-center justify-center gap-3 mb-6">
              <Vernie pose="waving" size={40} />
              <div
                className="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium"
                style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}
              >
                <span className="h-1.5 w-1.5 rounded-full" style={{ background: 'var(--accent)' }}></span>
                7 companies &middot; 4 industries &middot; your data stays in-house
              </div>
            </div>
            <h1 className="serif text-4xl sm:text-5xl md:text-6xl font-bold leading-[1.1] tracking-tight mb-6" style={{ color: 'var(--text)' }}>
              Stop reading filings.
              <br />
              Start <span style={{ color: 'var(--accent)' }}>understanding variance.</span>
            </h1>
            <p className="text-lg md:text-xl leading-relaxed mb-9 max-w-2xl mx-auto" style={{ color: 'var(--text-dim)' }}>
              Ask why the number moved — in plain English, with the exact page cited, every time.
            </p>
            <div className="flex items-center justify-center gap-3 mb-4">
              <a href="#demo" className="px-6 py-3.5 rounded-xl text-sm font-semibold btn-primary">
                Try a sample analysis
              </a>
              <a href="https://github.com/redsandr/rag-variance-explainer" className="px-6 py-3.5 rounded-xl text-sm font-medium btn-secondary">
                View on GitHub
              </a>
            </div>
          </div>

          <div className="mx-auto max-w-5xl w-full relative z-10 mt-14 md:mt-20">
            <HeroIllustration />
          </div>

          <div ref={statsRef} className="mx-auto max-w-4xl w-full relative z-10 mt-16 md:mt-20">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-4 text-center">
              {HERO_STATS.map((s, i) => (
                <div key={s.label}>
                  <div className="serif text-3xl md:text-5xl font-bold tabular" style={{ color: i === 0 ? 'var(--accent)' : 'var(--text)' }}>
                    {s.format(statValues[i])}
                  </div>
                  <div className="text-xs mt-2" style={{ color: 'var(--text-mute)' }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* TRUST BAR */}
        <section className="px-6 pb-20 md:pb-28">
          <div className="max-w-6xl mx-auto rounded-2xl card px-6 py-6 md:px-10 md:py-7">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-6">
              {TRUST_ITEMS.map((item) => (
                <div key={item} className="flex items-center gap-2.5">
                  <span
                    className="flex items-center justify-center h-5 w-5 rounded-full shrink-0"
                    style={{ background: 'var(--accent-soft)', color: 'var(--accent)' }}
                  >
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <path d="M5 13l4 4L19 7" />
                    </svg>
                  </span>
                  <span className="text-sm font-medium" style={{ color: 'var(--text-dim)' }}>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* PROBLEM */}
        <section className="max-w-4xl mx-auto px-6 py-24 md:py-32">
          <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>The problem</div>
          <p className="serif text-2xl md:text-3xl font-semibold leading-tight mb-6">
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

        {/* PROBLEM VS SOLUTION */}
        <section id="difference" ref={diffRef} className="max-w-6xl mx-auto px-6 pb-24 md:pb-32">
          <div className="mb-14 text-center">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>The difference</div>
            <p className="serif text-3xl md:text-4xl font-bold">Typical RAG vs. this pipeline.</p>
          </div>
          <div className="relative grid md:grid-cols-2 gap-5">
            {/* VS badge, centered over the seam on desktop */}
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

            {/* Typical RAG — muted, gray, blurry */}
            <div
              className="rounded-2xl p-6 md:p-8"
              style={{
                background: 'var(--surface)',
                border: '1px solid #333',
                opacity: diffVisible ? 0.68 : 0,
                transform: diffVisible ? 'translateX(0)' : 'translateX(-48px)',
                transition: 'transform 0.7s cubic-bezier(0.16,1,0.3,1), opacity 0.7s ease',
              }}
            >
              <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: '#666' }}>Typical RAG</div>
              <p
                className="text-sm leading-relaxed mb-5"
                style={{ color: '#8a8a8a', filter: 'blur(0.4px)', textShadow: '0 0 1px rgba(255,255,255,0.15)' }}
              >
                &quot;Labor costs increased due to various operational factors during the period.&quot;
              </p>
              <div className="flex items-center gap-2 text-xs font-medium" style={{ color: '#666' }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <path d="M15 9l-6 6M9 9l6 6" />
                </svg>
                No source. No confidence.
              </div>
            </div>

            {/* Our approach — gold, sharp, glowing */}
            <div
              className="rounded-2xl p-6 md:p-8 card-hover"
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

        {/* SAMPLE ANALYSIS DEMO */}
        <section id="demo" className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14 text-center">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Try it</div>
            <p className="serif text-3xl md:text-4xl font-bold mb-4">Pick a question. See the answer.</p>
            <p className="text-base max-w-xl mx-auto" style={{ color: 'var(--text-dim)' }}>
              Sample output from real questions the tool was tested on — no install required.
            </p>
          </div>

          <div className="flex flex-wrap justify-center gap-2.5 mb-8">
            {DEMO_ANALYSES.map((d) => (
              <button
                key={d.id}
                onClick={() => runDemo(d.id)}
                className="px-4 py-2.5 rounded-xl text-sm font-medium text-left"
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

          <div className="rounded-2xl card p-6 md:p-8 max-w-2xl mx-auto">
            {demoLoading ? (
              <div className="flex items-center gap-3 py-10 justify-center" style={{ color: 'var(--text-mute)' }}>
                <span className="mono text-sm">Analyzing filing</span>
                <span className="cursor-blink mono text-sm">&#9608;</span>
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

        {/* HOW IT WORKS */}
        <section id="how" ref={howRef} className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14 text-center">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>How it works</div>
            <p className="serif text-3xl md:text-4xl font-bold">Ask. Retrieve. Answer.</p>
          </div>

          <div className="rounded-2xl card p-4 sm:p-8 md:p-10">
            <div className="mono text-sm mb-8 text-center" style={{ color: 'var(--text-dim)', minHeight: 24 }}>
              <span style={{ color: 'var(--accent)' }}>&gt;</span> {pipeTyped}
              <span className="cursor-blink">&#9608;</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 md:gap-4 mb-8 relative">
              {PIPE_STEPS.map((step, i) => (
                <div key={step.title} className="relative">
                  <div className={`pipe-node rounded-xl p-3 sm:p-4 text-center ${activeStep >= i ? 'active' : ''}`}>
                    <div
                      className="mx-auto mb-2 flex items-center justify-center h-8 w-8 rounded-lg transition-colors duration-300"
                      style={{
                        background: activeStep >= i ? 'var(--accent-soft)' : 'var(--surface-alt)',
                        color: activeStep >= i ? 'var(--accent)' : 'var(--text-mute)',
                      }}
                    >
                      {PIPE_ICONS[step.icon]}
                    </div>
                    <div className="text-xs font-semibold mb-2">{step.title}</div>
                    <div
                      className="mono text-lg font-bold tabular"
                      style={{ color: i === 2 && activeStep >= 2 ? 'var(--accent)' : activeStep >= 3 && i === 3 ? 'var(--text)' : 'var(--text-mute)' }}
                    >
                      {stepValues[i]}
                    </div>
                    <div className="text-[10px] mt-1" style={{ color: 'var(--text-mute)' }}>{step.label}</div>
                  </div>
                  {/* Connecting arrow, drawn on when this step becomes active */}
                  {i < PIPE_STEPS.length - 1 && (
                    <svg
                      className="hidden sm:block absolute pointer-events-none"
                      style={{ top: '20%', left: '100%', width: 'calc(0.5rem + 1rem)', height: 12, transform: 'translateX(-4px)' }}
                      viewBox="0 0 24 12"
                    >
                      <path
                        d="M0 6h16"
                        fill="none"
                        stroke="var(--accent)"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeDasharray="16"
                        strokeDashoffset={activeStep > i ? 0 : 16}
                        style={{ transition: 'stroke-dashoffset 0.5s ease' }}
                      />
                      <path
                        d="M14 2l5 4-5 4"
                        fill="none"
                        stroke="var(--accent)"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        style={{ opacity: activeStep > i ? 1 : 0, transition: 'opacity 0.3s ease 0.3s' }}
                      />
                    </svg>
                  )}
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
              className="relative rounded-xl p-4 transition-opacity duration-300"
              style={{
                background: 'var(--accent-soft)',
                border: '1px solid var(--border-strong)',
                boxShadow: pipeOutputVisible ? '0 0 40px -10px rgba(212,175,55,0.45)' : 'none',
                opacity: pipeOutputVisible ? 1 : 0,
              }}
            >
              {/* Vernie peeking from behind the finished answer card */}
              <div
                className="hidden sm:block absolute -top-5 -right-3"
                style={{
                  opacity: pipeOutputVisible ? 1 : 0,
                  transform: pipeOutputVisible ? 'translateY(0)' : 'translateY(8px)',
                  transition: 'opacity 0.4s ease 0.2s, transform 0.4s ease 0.2s',
                }}
              >
                <Vernie pose="found" size={36} />
              </div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className="text-xs font-semibold" style={{ color: 'var(--accent)' }}>Sourced answer ready</span>
              </div>
              <p className="text-xs leading-relaxed" style={{ color: 'var(--accent)' }}>
                Wage inflation and CA minimum wage increases, offset by sales leverage. Cited: CMG 10-K p.34, 10-Q p.12.
              </p>
            </div>
          </div>
        </section>

        {/* EVIDENCE */}
        <section id="evidence" className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Evidence, not claims</div>
            <p className="serif text-3xl md:text-4xl font-bold mb-4">Accuracy, tested and measured.</p>
            <p className="text-base max-w-2xl" style={{ color: 'var(--text-dim)' }}>
              Tested against 40 real questions with known correct answers, before and after adding a relevance-ranking
              step. The hardest cases went from being missed entirely to found first.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {METRICS.map((m) => (
              <div key={m.label} className="rounded-2xl p-5 card">
                <div className="text-3xl font-bold tabular mb-1" style={{ color: 'var(--accent)' }}>{m.value}</div>
                <div className="text-sm font-medium mb-1">{m.label}</div>
                <div className="text-xs" style={{ color: 'var(--text-mute)' }}>{m.sub}</div>
              </div>
            ))}
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
              <div>
                <div className="text-sm font-semibold mb-1">Right source found on the first try</div>
                <div className="text-xs" style={{ color: 'var(--text-mute)' }}>Before vs. after adding a relevance-ranking step</div>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'var(--border-strong)' }}></span>
                <span style={{ color: 'var(--text-dim)' }}>Before ranking step</span>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="h-2.5 w-2.5 rounded-sm" style={{ background: 'var(--accent)' }}></span>
                <span style={{ color: 'var(--text-dim)' }}>After ranking step</span>
              </div>
              <div className="pt-3">
                <div className="text-3xl font-bold tabular" style={{ color: 'var(--accent)' }}>0.52 &rarr; 0.66</div>
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
                <span className="font-semibold" style={{ color: 'var(--accent)' }}>now #1</span>
              </div>
            </div>
            <div className="rounded-xl p-5 card card-hover">
              <div className="mono text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Cracker Barrel labor-cost question</div>
              <div className="flex items-center gap-3 text-sm">
                <span style={{ color: 'var(--text-mute)' }}>was result #17</span>
                <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
                <span className="font-semibold" style={{ color: 'var(--accent)' }}>now #1</span>
              </div>
            </div>
            <div className="rounded-xl p-5 card card-hover">
              <div className="mono text-xs mb-2" style={{ color: 'var(--text-mute)' }}>Questions it used to miss entirely</div>
              <div className="flex items-center gap-3 text-sm">
                <span style={{ color: 'var(--text-mute)' }}>4 of 20</span>
                <span style={{ color: 'var(--text-mute)' }}>&rarr;</span>
                <span className="font-semibold" style={{ color: 'var(--accent)' }}>0 of 20</span>
              </div>
            </div>
          </div>
        </section>

        {/* USE CASES */}
        <section className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Use cases</div>
            <p className="serif text-3xl md:text-4xl font-bold">Real questions, real answers.</p>
          </div>
          <div className="rounded-2xl overflow-hidden card hidden md:block">
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
                        style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}
                      >
                        {uc.src}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile: stacked cards instead of a squeezed table */}
          <div className="space-y-3 md:hidden">
            {USE_CASES.map((uc) => (
              <div key={uc.q} className="rounded-xl p-4 card">
                <div className="text-sm font-medium mb-2">{uc.q}</div>
                <div className="text-sm mb-3" style={{ color: 'var(--text-dim)' }}>{uc.a}</div>
                <span
                  className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                  style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}
                >
                  {uc.src}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* FEATURES */}
        <section id="features" className="max-w-6xl mx-auto px-6 py-24 md:py-32">
          <div className="mb-14">
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Why financial teams use it</div>
            <p className="serif text-3xl md:text-4xl font-bold">Built for accuracy, security, and trust.</p>
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
            <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>For engineers &amp; reviewers</div>
            <p className="serif text-3xl md:text-4xl font-bold">Running in two minutes.</p>
            <p className="text-base mt-3" style={{ color: 'var(--text-dim)' }}>Want to run it yourself or see exactly how it works under the hood? Here&apos;s the full setup.</p>
          </div>
          <div className="rounded-2xl overflow-hidden card">
            <div className="flex flex-wrap items-center justify-between gap-y-2 gap-x-3 px-2 sm:px-0" style={{ borderBottom: '1px solid var(--border)' }}>
              <div className="flex flex-wrap">
                {['local', 'openai', 'claude'].map((t) => (
                  <button
                    key={t}
                    className={`tab-btn px-3 sm:px-6 py-3 text-sm font-medium ${tab === t ? 'active' : ''}`}
                    style={{ borderBottom: tab === t ? '2px solid var(--accent)' : '2px solid transparent' }}
                    onClick={() => setTab(t)}
                  >
                    {t === 'local' ? 'Local model' : t === 'openai' ? 'OpenAI API' : 'Claude API'}
                  </button>
                ))}
              </div>
              <button
                className="copy-btn flex items-center gap-1.5 mb-2 sm:mb-0 sm:mr-4 px-3 py-1.5 rounded-lg text-xs font-medium"
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
            <p className="serif text-3xl md:text-4xl font-bold">What&apos;s next.</p>
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
          <div className="flex items-center gap-3 text-sm" style={{ color: 'var(--text-mute)' }}>
            <Vernie pose="idle" size={32} />
            <span>MIT License</span><span>&middot;</span><span>2026</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <a href="#how" className="nav-link">Methodology</a>
            <a href="https://github.com/redsandr/rag-variance-explainer" className="nav-link">GitHub</a>
            <a href="https://github.com/redsandr/rag-variance-explainer/tree/master/docs" className="nav-link">Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}