import { useEffect, useRef, useState } from 'react';
import Head from 'next/head';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import MethodExplorer from '../components/MethodExplorer';
import EvidenceSequence from '../components/EvidenceSequence';
import SetupGuide from '../components/SetupGuide';

const repository = 'https://github.com/redsandr/rag-variance-explainer';
const questions = [
  { question: 'Can I try a verified analysis here?', answer: 'Not yet. This page illustrates the research workflow, but no filing-backed example has been approved for publication. The demo panel shows the current review status.' },
  { question: 'Does a matching quote prove why a metric changed?', answer: 'No. The verifier checks that quoted words occur in retrieved text. An analyst must still check the metric, reporting period, arithmetic and causal language in the original SEC filing.' },
  { question: 'Can I run the project on my computer?', answer: 'Yes. The open-source repository includes a Streamlit interface and local setup instructions. You need Python 3.11, an LLM backend, a descriptive SEC user agent and time to build the index.' },
  { question: 'Is this a hosted service or financial advice?', answer: 'No. It is a local, single-user research prototype and a portfolio case study. Do not rely on an unreviewed answer for an investment decision.' },
];

function Arrow({ diagonal = false }) {
  return <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" fill="none"><path d={diagonal ? 'M4 14 14 4M6 4h8v8' : 'M2 9h13m-5-5 5 5-5 5'} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

export default function Home() {
  const [theme, setTheme] = useState('dark');
  const [themeReady, setThemeReady] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuButton = useRef(null);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    const saved = window.localStorage.getItem('variance-theme');
    if (saved === 'light') setTheme('light');
    setThemeReady(true);
  }, []);
  useEffect(() => { if (themeReady) document.documentElement.dataset.theme = theme; }, [theme, themeReady]);
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
    <a className="skip-link" href="#main-content">Skip to content</a>
    <header className="site-header wrap">
      <a className="brand" href="#top" aria-label="Variance Explainer, back to top" onClick={() => setMenuOpen(false)}><span className="brand-mark" aria-hidden="true"><span></span><span></span></span><span>Variance Explainer</span></a>
      <nav className="nav-links" aria-label="Main navigation"><a href="#tour">How it works</a><a href="#demo">Demo status</a><a href="#method">The method</a><a href="#setup">Install</a><a href="#faq">FAQ</a></nav>
      <div className="header-controls"><button type="button" className="theme-switch" aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`} onClick={toggleTheme}><svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3.5" stroke="currentColor" strokeWidth="1.5" /><path d="M10 1.5v2m0 13v2M1.5 10h2m13 0h2M4 4l1.5 1.5m9 9L16 16M16 4l-1.5 1.5m-9 9L4 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg></button><a className="header-action" href="#demo">View demo <Arrow /></a><button ref={menuButton} className="menu-toggle" type="button" aria-expanded={menuOpen} aria-controls="mobile-menu" aria-label={menuOpen ? 'Close menu' : 'Open menu'} onClick={() => setMenuOpen(!menuOpen)}><span></span><span></span></button></div>
      <AnimatePresence initial={false}>{menuOpen && <motion.nav id="mobile-menu" className="mobile-menu" aria-label="Mobile navigation" initial={reducedMotion ? false : { opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }} transition={{ duration: reducedMotion ? 0 : .2 }}><a href="#tour" onClick={() => setMenuOpen(false)}>How it works <Arrow /></a><a href="#demo" onClick={() => setMenuOpen(false)}>Demo status <Arrow /></a><a href="#method" onClick={() => setMenuOpen(false)}>The method <Arrow /></a><a href="#setup" onClick={() => setMenuOpen(false)}>Install locally <Arrow /></a><a href="#faq" onClick={() => setMenuOpen(false)}>FAQ <Arrow /></a><a href={repository} target="_blank" rel="noopener noreferrer" onClick={() => setMenuOpen(false)}>Source on GitHub <Arrow diagonal /></a></motion.nav>}</AnimatePresence>
    </header>
    <main id="main-content" tabIndex={-1}>
      <section className="hero wrap" aria-labelledby="hero-title"><div className="hero-ghost" aria-hidden="true">VARIANCE / EXAMINED</div><div className="hero-copy"><div className="hero-signal"><span className="hero-signal-dot" /> SEC FILING RESEARCH · LOCAL PROTOTYPE</div><h1 id="hero-title">Ask why <span>revenue, margin,<br />{' '}or labor cost</span> changed.</h1><p>Follow a financial question through the filing. Stop where the evidence stops.</p><div className="hero-live" aria-label="Illustrative question: Why did revenue change?"><span className="hero-live-label" aria-hidden="true">ILLUSTRATIVE QUESTION</span><span className="hero-live-prompt" aria-hidden="true">$ ask &quot;Why did revenue change?&quot;</span></div><div className="hero-actions"><a className="primary-action" href="#tour">Watch the research flow <Arrow /></a><a className="secondary-action" href="#setup">Run it locally <Arrow diagonal /></a></div></div></section>
      <EvidenceSequence />
      <section className="workpaper wrap" id="demo" aria-labelledby="demo-title"><div className="paper-heading"><span className="window-dots" aria-hidden="true"><i></i><i></i><i></i></span><span>Research workpaper</span><span>Illustrative workflow / no verified answer</span></div><div className="paper-body"><div className="paper-question"><span className="field-label">The starting question</span><h2 id="demo-title">Why did the metric change?</h2><p>Research begins with a question. An answer is withheld until its passages and the original filing have been reviewed.</p><div className="paper-path"><span>Retrieve a passage</span><Arrow /><span>Check the quote</span><Arrow /><span>Read the filing</span></div></div><div className="paper-review"><div className="review-top"><span className="field-label">Source review</span><span className="pending">Pending review</span></div><div className="review-main"><span className="review-symbol" aria-hidden="true"><svg width="56" height="56" viewBox="0 0 56 56" fill="none"><path d="M13 8h22l8 8v32H13V8Z" stroke="currentColor" strokeWidth="1.5" /><path d="M35 8v9h8M20 26h16M20 33h12M20 40h8" stroke="currentColor" strokeWidth="1.5" /></svg></span><h3>No approved case yet.</h3><p>The earlier sample answers, filing page references and confidence scores have not been verified against the original filings. They are not presented as evidence here.</p></div><div className="review-foot">A filing-backed example will appear after manual review.</div></div></div></section>
      <section className="method wrap" id="method" aria-labelledby="method-title"><div className="section-intro"><h2 id="method-title">The method is only as strong as its source.</h2><p>Explore each research step. The last decision still belongs to an analyst reading the original disclosure.</p></div><MethodExplorer /></section>
      <section className="limits" id="limits" aria-labelledby="limits-title"><div className="wrap limits-inner"><div><h2 id="limits-title">A citation is a starting point.<br /><span>Not a verdict.</span></h2></div><div className="limits-copy"><p>This is a local research prototype, not a public hosted analysis service. A quote check confirms that words appear in retrieved text. It does not independently validate the arithmetic or establish a cause.</p><p>The index covers selected US companies and periods. A reviewed demo and measured results are still being prepared. Until then, no response here is represented as filing-verified.</p><a href={repository} target="_blank" rel="noopener noreferrer">Explore the project and setup <Arrow diagonal /></a></div></div></section>
      <SetupGuide repository={repository} />
      <section className="faq wrap" id="faq" aria-labelledby="faq-title"><div className="faq-heading"><h2 id="faq-title">Questions worth asking.</h2><p>What the prototype can show, and what still needs a human check.</p></div><div className="faq-list">{questions.map(({ question, answer }) => <details key={question}><summary>{question}<span aria-hidden="true">+</span></summary><p>{answer}</p></details>)}</div></section>
      <section className="closing wrap"><span className="closing-mark" aria-hidden="true">◇</span><h2>Read the source.<br /><span>Then decide.</span></h2><a className="primary-action" href="#demo">Return to demo status <Arrow /></a></section>
    </main><footer className="site-footer wrap"><a className="brand" href="#top"><span className="brand-mark" aria-hidden="true"><span></span><span></span></span><span>Variance Explainer</span></a><span>Independent research prototype. Verify against the original filing.</span><a href="#top">Back to top ↑</a></footer>
  </div>;
}
