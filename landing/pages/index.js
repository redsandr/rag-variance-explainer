import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import MethodExplorer from '../components/MethodExplorer';

const repository = 'https://github.com/redsandr/rag-variance-explainer';
const trail = [
  { name: 'Question', title: 'Start with the change.', copy: 'Ask what changed in a selected company and reporting period. A question is a research prompt, not a conclusion.' },
  { name: 'Passage', title: 'Find the disclosure.', copy: 'Search relevant Management Discussion and Analysis passages in indexed SEC filings.' },
  { name: 'Quote check', title: 'Check the wording.', copy: 'Compare quoted words with retrieved text. A match does not verify arithmetic or explain causation.' },
  { name: 'Filing review', title: 'Return to the source.', copy: 'Review the original filing before using an explanation. No example on this site has passed that review yet.' },
];

function Arrow({ diagonal = false }) {
  return <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" fill="none"><path d={diagonal ? 'M4 14 14 4M6 4h8v8' : 'M2 9h13m-5-5 5 5-5 5'} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

function EvidenceTrail() {
  const [active, setActive] = useState(0);
  const reducedMotion = useReducedMotion();
  return <section className="trail-band" aria-labelledby="trail-title">
    <div className="wrap trail-inner">
      <div className="trail-heading"><h2 id="trail-title">One question.<br /><em>Every step visible.</em></h2><p>Select a stage to see what it establishes and where the evidence stops.</p></div>
      <div className="trail-interaction">
        <div className="trail-tabs" aria-label="Evidence trail stages">
          {trail.map((step, index) => <button type="button" key={step.name} aria-pressed={active === index} aria-controls="trail-detail" onClick={() => setActive(index)} className={`trail-tab ${active === index ? 'selected' : ''}`}>
            <span className="trail-point" aria-hidden="true">{active === index && <motion.span layoutId="trail-indicator" transition={reducedMotion ? { duration: 0 } : { type: 'spring', stiffness: 400, damping: 36 }} />}</span><span>{step.name}</span>
          </button>)}
        </div>
        <div id="trail-detail" className="trail-detail" aria-live="polite" aria-atomic="true">
          <AnimatePresence mode="wait" initial={false}><motion.div key={active} initial={reducedMotion ? false : { opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 1 } : { opacity: 0, y: -8 }} transition={{ duration: reducedMotion ? 0 : .22 }}><span className="trail-counter">Stage 0{active + 1} / 04</span><h3>{trail[active].title}</h3><p>{trail[active].copy}</p></motion.div></AnimatePresence>
        </div>
      </div>
    </div>
  </section>;
}

export default function Home() {
  const [theme, setTheme] = useState('dark');
  const [menuOpen, setMenuOpen] = useState(false);
  const menuButton = useRef(null);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const saved = window.localStorage.getItem('variance-theme');
    if (saved === 'light') setTheme('light');
  }, []);
  useEffect(() => { document.documentElement.dataset.theme = theme; }, [theme]);
  useEffect(() => {
    if (!menuOpen) return;
    const onEscape = (event) => { if (event.key === 'Escape') { setMenuOpen(false); menuButton.current?.focus(); } };
    window.addEventListener('keydown', onEscape);
    return () => window.removeEventListener('keydown', onEscape);
  }, [menuOpen]);

  const toggleTheme = () => {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    window.localStorage.setItem('variance-theme', next);
  };

  return <div className="site-shell" id="top">
    <Head><title>Variance Explainer | Investigate changes in SEC filings</title><meta name="description" content="Explore how a financial research prototype investigates changes in SEC filings and why original filing review matters." /><meta name="theme-color" content={theme === 'dark' ? '#121310' : '#f6f4ed'} /></Head>
    <header className="site-header wrap">
      <a className="brand" href="#top" aria-label="Variance Explainer, back to top" onClick={() => setMenuOpen(false)}><span className="brand-mark" aria-hidden="true"><span></span><span></span></span><span>Variance Explainer</span></a>
      <nav className="nav-links" aria-label="Main navigation"><a href="#method">The method</a><a href="#limits">Evidence policy</a><a href={repository} target="_blank" rel="noopener noreferrer">GitHub <Arrow diagonal /></a></nav>
      <div className="header-controls"><button type="button" className="theme-switch" aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`} onClick={toggleTheme}><svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3.5" stroke="currentColor" strokeWidth="1.5" /><path d="M10 1.5v2m0 13v2M1.5 10h2m13 0h2M4 4l1.5 1.5m9 9L16 16M16 4l-1.5 1.5m-9 9L4 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg></button><a className="header-action" href="#demo">View demo <Arrow /></a><button ref={menuButton} className="menu-toggle" type="button" aria-expanded={menuOpen} aria-controls="mobile-menu" aria-label={menuOpen ? 'Close menu' : 'Open menu'} onClick={() => setMenuOpen(!menuOpen)}><span></span><span></span></button></div>
      <AnimatePresence initial={false}>{menuOpen && <motion.nav id="mobile-menu" className="mobile-menu" aria-label="Mobile navigation" initial={reducedMotion ? false : { opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }} transition={{ duration: reducedMotion ? 0 : .2 }}><a href="#demo" onClick={() => setMenuOpen(false)}>Demo status <Arrow /></a><a href="#method" onClick={() => setMenuOpen(false)}>The method <Arrow /></a><a href="#limits" onClick={() => setMenuOpen(false)}>Evidence policy <Arrow /></a><a href={repository} target="_blank" rel="noopener noreferrer" onClick={() => setMenuOpen(false)}>Source on GitHub <Arrow diagonal /></a></motion.nav>}</AnimatePresence>
    </header>
    <main>
      <section className="hero wrap" aria-labelledby="hero-title"><div className="hero-copy"><h1 id="hero-title">Ask why it changed.<br /><span>Follow the evidence.</span></h1><p>Investigate changes in SEC filings through retrieved MD&amp;A passages. If the filing does not establish a cause, the answer remains open.</p><div className="hero-actions"><a className="primary-action" href="#demo">Explore the demo status <Arrow /></a><span>A reviewed example is being prepared.</span></div></div><div className="hero-side" aria-hidden="true"><div className="hero-side-orbit"><span>10-K</span><span>MD&amp;A</span><span>10-Q</span></div><div className="hero-side-caption">QUESTION <span>→</span> PASSAGE <span>→</span> REVIEW</div></div></section>
      <EvidenceTrail />
      <section className="workpaper wrap" id="demo" aria-labelledby="demo-title"><div className="paper-heading"><span className="window-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>Research workpaper</span><span>Illustrative workflow / no verified answer</span></div><div className="paper-body"><div className="paper-question"><span className="field-label">The starting question</span><h2 id="demo-title">Why did the metric change?</h2><p>Research begins with a question. An answer is withheld until its passages and the original filing have been reviewed.</p><div className="paper-path"><span>Retrieve a passage</span><Arrow /><span>Check the quote</span><Arrow /><span>Read the filing</span></div></div><div className="paper-review"><div className="review-top"><span className="field-label">Source review</span><span className="pending">Pending review</span></div><div className="review-main"><span className="review-symbol" aria-hidden="true"><svg width="56" height="56" viewBox="0 0 56 56" fill="none"><path d="M13 8h22l8 8v32H13V8Z" stroke="currentColor" strokeWidth="1.5" /><path d="M35 8v9h8M20 26h16M20 33h12M20 40h8" stroke="currentColor" strokeWidth="1.5" /></svg></span><h3>No approved case yet.</h3><p>The earlier sample answers, filing page references and confidence scores have not been verified against the original filings. They are not presented as evidence here.</p></div><div className="review-foot">A filing-backed example will appear after manual review.</div></div></div></section>
      <section className="method wrap" id="method" aria-labelledby="method-title"><div className="section-intro"><h2 id="method-title">The method is only as strong as its source.</h2><p>Explore each research step. The last decision still belongs to an analyst reading the original disclosure.</p></div><MethodExplorer /></section>
      <section className="limits" id="limits" aria-labelledby="limits-title"><div className="wrap limits-inner"><div><h2 id="limits-title">A citation is a starting point.<br /><span>Not a verdict.</span></h2></div><div className="limits-copy"><p>This is a local research prototype, not a public hosted analysis service. A quote check confirms that words appear in retrieved text. It does not independently validate the arithmetic or establish a cause.</p><p>The index covers selected US companies and periods. A reviewed demo and measured results are still being prepared. Until then, no response here is represented as filing-verified.</p><a href={repository} target="_blank" rel="noopener noreferrer">Explore the project and setup <Arrow diagonal /></a></div></div></section>
      <section className="closing wrap"><span className="closing-mark" aria-hidden="true">◇</span><h2>Read the source.<br /><span>Then decide.</span></h2><a className="primary-action" href="#demo">Return to demo status <Arrow /></a></section>
    </main><footer className="site-footer wrap"><a className="brand" href="#top"><span className="brand-mark" aria-hidden="true"><span></span><span></span></span><span>Variance Explainer</span></a><span>Independent research prototype. Verify against the original filing.</span><a href="#top">Back to top ↑</a></footer>
  </div>;
}
