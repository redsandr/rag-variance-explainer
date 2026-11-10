import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';

export const repositoryUrl = 'https://github.com/redsandr/rag-variance-explainer';

const navigation = [
  { href: '/example', label: 'Example', id: 'example' },
  { href: '/method', label: 'How it works', id: 'method' },
  { href: '/install', label: 'Install', id: 'install' },
  { href: '/about', label: 'About', id: 'about' },
  { href: '/contact', label: 'Request a case', id: 'contact' },
];

export function ArrowIcon({ diagonal = false }) {
  return <svg aria-hidden="true" width="18" height="18" viewBox="0 0 18 18" fill="none"><path d={diagonal ? 'M4 14 14 4M6 4h8v8' : 'M2 9h13m-5-5 5 5-5 5'} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

export default function SiteLayout({ children, active = '' }) {
  const [theme, setTheme] = useState('dark');
  const [menuOpen, setMenuOpen] = useState(false);
  const menuButton = useRef(null);
  const reducedMotion = useReducedMotion();

  useEffect(() => {
    let saved;
    try { saved = window.localStorage.getItem('variance-theme'); } catch { saved = null; }
    const initial = saved === 'light' ? 'light' : 'dark';
    document.documentElement.dataset.theme = initial;
    setTheme(initial);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    function onEscape(event) {
      if (event.key === 'Escape') {
        setMenuOpen(false);
        menuButton.current?.focus();
      }
    }
    window.addEventListener('keydown', onEscape);
    return () => window.removeEventListener('keydown', onEscape);
  }, [menuOpen]);

  function toggleTheme() {
    const next = theme === 'dark' ? 'light' : 'dark';
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try { window.localStorage.setItem('variance-theme', next); } catch {}
  }

  return <div className="site-shell" id="top">
    <a className="skip-link" href="#main-content">Skip to content</a>
    <header className="site-header wrap">
      <a className="brand" href="/" aria-label="Variance Explainer, home" onClick={() => setMenuOpen(false)}><span className="brand-mark" aria-hidden="true"><span /><span /></span><span>Variance Explainer</span></a>
      <nav className="nav-links" aria-label="Main navigation">
        {navigation.map((item) => <a key={item.id} href={item.href} aria-current={active === item.id ? 'page' : undefined}>{item.label}</a>)}
      </nav>
      <div className="header-controls">
        <button type="button" className="theme-switch" aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`} onClick={toggleTheme}>
          <svg aria-hidden="true" width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3.5" stroke="currentColor" strokeWidth="1.5" /><path d="M10 1.5v2m0 13v2M1.5 10h2m13 0h2M4 4l1.5 1.5m9 9L16 16M16 4l-1.5 1.5m-9 9L4 16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /></svg>
        </button>
        <a className="header-action" href="/example">Explore example <ArrowIcon /></a>
        <button ref={menuButton} className="menu-toggle" type="button" aria-expanded={menuOpen} aria-controls="mobile-menu" aria-label={menuOpen ? 'Close menu' : 'Open menu'} onClick={() => setMenuOpen(!menuOpen)}><span /><span /></button>
      </div>
      <AnimatePresence initial={false}>{menuOpen && <motion.nav id="mobile-menu" className="mobile-menu" aria-label="Mobile navigation" initial={reducedMotion ? false : { opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }} transition={{ duration: reducedMotion ? 0 : .2 }}>
        {navigation.map((item) => <a key={item.id} href={item.href} aria-current={active === item.id ? 'page' : undefined} onClick={() => setMenuOpen(false)}>{item.label}<ArrowIcon /></a>)}
        <a href={repositoryUrl} target="_blank" rel="noopener noreferrer" onClick={() => setMenuOpen(false)}>Source on GitHub<ArrowIcon diagonal /></a>
      </motion.nav>}</AnimatePresence>
    </header>
    <main id="main-content" tabIndex={-1}>{children}</main>
    <footer className="site-footer wrap">
      <div><a className="brand" href="/"><span className="brand-mark" aria-hidden="true"><span /><span /></span><span>Variance Explainer</span></a><p>Independent research prototype. Not investment advice.</p></div>
      <nav aria-label="Footer navigation"><a href="/method">Method</a><a href="/install">Install</a><a href="/about">About</a><a href="/contact">Contact</a><a href={repositoryUrl} target="_blank" rel="noopener noreferrer">GitHub</a></nav>
    </footer>
  </div>;
}
