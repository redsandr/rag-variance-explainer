import { useEffect, useRef, useState, useCallback } from 'react';
import Vernie from './Vernie';
import useTypewriter from '../hooks/useTypewriter';
import { PIPE_QUESTION, PIPE_STEPS, PIPE_ICONS } from '../data/constants';

export default function HowItWorks() {
  const howRef = useRef(null);
  const timersRef = useRef([]);
  const rafRef = useRef(null);
  const mountedRef = useRef(true);
  const [pipelineKey, setPipelineKey] = useState(0);
  const [activeStep, setActiveStep] = useState(-1);
  const [stepValues, setStepValues] = useState(['—', '—', '—', '—']);
  const [pipeOutputVisible, setPipeOutputVisible] = useState(false);
  const [pipelineRunning, setPipelineRunning] = useState(false);

  const clearAllTimers = useCallback(() => {
    timersRef.current.forEach(clearTimeout);
    timersRef.current = [];
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
  }, []);

  const pipeTyped = useTypewriter(
    PIPE_QUESTION,
    {
      startDelay: 0,
      speed: 28,
      onDone: () => {
        const t = setTimeout(() => {
          if (mountedRef.current) setActiveStep(0);
        }, 300);
        timersRef.current.push(t);
      },
    },
    [pipelineKey]
  );

  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  function animateCount(idx, from, to, duration, isScore = false) {
    const start = performance.now();
    function frame(now) {
      if (!mountedRef.current) return;
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      const val = from + (to - from) * eased;
      setStepValues((prev) => {
        const next = [...prev];
        next[idx] = isScore ? val.toFixed(2) : String(Math.round(val));
        return next;
      });
      if (t < 1) rafRef.current = requestAnimationFrame(frame);
    }
    rafRef.current = requestAnimationFrame(frame);
  }

  useEffect(() => {
    clearAllTimers();
    if (activeStep < 0) return;
    if (activeStep >= PIPE_STEPS.length) {
      const t1 = setTimeout(() => {
        if (mountedRef.current) setPipeOutputVisible(true);
      }, 200);
      const t2 = setTimeout(() => {
        if (!mountedRef.current) return;
        if (pipelineRunning) {
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
        if (!mountedRef.current) return clearInterval(interval);
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

    const t = setTimeout(() => {
      if (mountedRef.current) setActiveStep((s) => s + 1);
    }, 750);
    timersRef.current.push(t);

    return clearAllTimers;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeStep, pipelineRunning]);

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

  return (
    <section id="how" ref={howRef} className="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32">
      <div className="mb-10 sm:mb-14 text-center">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>How it works</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold">Ask. Retrieve. Answer.</p>
      </div>

      <div className="rounded-2xl card p-4 sm:p-8 md:p-10">
        <div className="mono text-xs sm:text-sm mb-8 text-center" style={{ color: 'var(--text-dim)', minHeight: 24 }}>
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
                  className="mono text-base sm:text-lg font-bold tabular truncate max-w-full"
                  style={{ color: i === 2 && activeStep >= 2 ? 'var(--accent)' : activeStep >= 3 && i === 3 ? 'var(--text)' : 'var(--text-mute)' }}
                >
                  {stepValues[i]}
                </div>
                <div className="text-[10px] mt-1" style={{ color: 'var(--text-mute)' }}>{step.label}</div>
              </div>
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
  );
}
