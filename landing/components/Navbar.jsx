import { useState, useEffect, useCallback } from 'react';

const NAV_LINKS = [
  { href: '#demo', label: 'Demo' },
  { href: '#how', label: 'How it works' },
  { href: '#evidence', label: 'Accuracy' },
  { href: '#faq', label: 'FAQ' },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [dark, setDark] = useState(true);

  function toggleTheme() {
    const el = document.documentElement;
    const next = !el.classList.contains('dark');
    el.classList.toggle('dark', next);
    setDark(next);
    try {
      localStorage.setItem('theme', next ? 'dark' : 'light');
    } catch (e) { /* ignore */ }
  }

  useEffect(() => {
    setDark(document.documentElement.classList.contains('dark'));
  }, []);

  const closeMenu = useCallback(() => setMenuOpen(false), []);

  useEffect(() => {
    if (!menuOpen) return;
    const handler = (e) => { if (e.key === 'Escape') closeMenu(); };
    document.addEventListener('keydown', handler);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handler);
      document.body.style.overflow = '';
    };
  }, [menuOpen, closeMenu]);

  return (
    <header
      className="fixed top-0 left-0 right-0 z-50"
      style={{
        borderBottom: '1px solid var(--border)',
        background: 'var(--header-bg)',
        backdropFilter: 'blur(14px)',
      }}
    >
      <div className="max-w-[1180px] mx-auto px-5 sm:px-7 h-16 flex items-center justify-between">
        <a href="#top" className="flex items-center gap-2.5 font-semibold tracking-tight">
          <span className="w-[26px] h-[26px] rounded-lg flex items-center justify-center shrink-0" style={{ background: 'var(--gold-grad)' }}>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#08080d" strokeWidth="2.5">
              <path d="M12 2 L22 8 L22 16 L12 22 L2 16 L2 8 Z" />
            </svg>
          </span>
          Variance Explainer
        </a>

        <div className="hidden md:flex items-center gap-6">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} className="mono text-xs" style={{ color: 'var(--text-dim)', transition: 'color 0.15s' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--text)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>
              <span style={{ color: 'var(--accent)' }}>/</span> {l.label}
            </a>
          ))}
          <a href="#demo" className="mono text-xs font-medium cta-pill">Try the demo</a>
          <button
            onClick={toggleTheme}
            aria-label={dark ? 'Switch to light mode' : 'Switch to dark mode'}
            className="flex items-center justify-center w-10 h-10 rounded-lg"
            style={{ border: '1px solid var(--border-strong)', color: 'var(--text-dim)' }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--accent)'; e.currentTarget.style.borderColor = 'var(--accent)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-dim)'; e.currentTarget.style.borderColor = 'var(--border-strong)'; }}
          >
            {dark ? (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <circle cx="12" cy="12" r="4" />
                <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" />
              </svg>
            ) : (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
              </svg>
            )}
          </button>
        </div>

        <button
          onClick={() => setMenuOpen(true)}
          className="md:hidden flex items-center justify-center rounded-lg p-2 min-w-[44px] min-h-[44px]"
          style={{ color: 'var(--text)' }}
          aria-label="Open menu"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <path d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Backdrop */}
      <div
        onClick={closeMenu}
        role="presentation"
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(4px)',
          opacity: menuOpen ? 1 : 0,
          pointerEvents: menuOpen ? 'auto' : 'none',
          transition: 'opacity 0.25s ease',
        }}
      />

      {/* Drawer */}
      <div
        role="dialog"
        aria-label="Navigation menu"
        style={{
          position: 'fixed',
          top: 0,
          right: 0,
          bottom: 0,
          width: 280,
          background: 'var(--surface)',
          borderLeft: '1px solid var(--border)',
          boxShadow: '-8px 0 40px rgba(0,0,0,0.5)',
          transform: menuOpen ? 'translateX(0)' : 'translateX(100%)',
          transition: 'transform 0.3s cubic-bezier(0.16,1,0.3,1)',
          zIndex: 60,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: '1px solid var(--border)' }}>
          <span className="text-sm font-semibold tracking-tight">Navigation</span>
          <button
            onClick={closeMenu}
            className="flex items-center justify-center rounded-lg p-2 min-w-[44px] min-h-[44px]"
            aria-label="Close menu"
            style={{ color: 'var(--text-dim)' }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div className="flex-1 px-3 py-4 flex flex-col gap-1.5">
          {NAV_LINKS.map((l) => (
            <a
              key={l.href}
              href={l.href}
              onClick={closeMenu}
              className="flex items-center min-h-[44px] px-4 rounded-xl text-sm font-medium transition-all"
              style={{ color: 'var(--text-dim)' }}
              onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--accent-soft)'; e.currentTarget.style.color = 'var(--text)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.background = ''; e.currentTarget.style.color = 'var(--text-dim)'; }}
            >
              <span style={{ color: 'var(--accent)' }}>/</span>&nbsp;{l.label}
            </a>
          ))}
          <div className="mt-3 px-4">
            <a
              href="#demo"
              onClick={closeMenu}
              className="block w-full text-center px-4 py-3 rounded-xl text-sm font-semibold"
              style={{ background: 'var(--gold-grad)', color: 'var(--btn-text-on-accent)' }}
            >
              Try the demo
            </a>
          </div>
          <div className="mt-2 px-4">
            <button
              onClick={() => { toggleTheme(); }}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl text-sm font-medium"
              style={{ border: '1px solid var(--border-strong)', color: 'var(--text-dim)' }}
            >
              {dark ? (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2" /></svg>
              ) : (
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" /></svg>
              )}
              {dark ? 'Light mode' : 'Dark mode'}
            </button>
          </div>
        </div>
        <div className="px-5 py-4 text-xs" style={{ borderTop: '1px solid var(--border)', color: 'var(--text-mute)' }}>
          MIT &middot; 2026
        </div>
      </div>
    </header>
  );
}