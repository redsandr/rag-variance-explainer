import { useState, useEffect, useCallback } from 'react';
import Vernie from './Vernie';

const NAV_LINKS = [
  { href: '#demo', label: 'Sample analysis' },
  { href: '#how', label: 'How it works' },
  { href: '#evidence', label: 'Evidence' },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

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
      style={{ background: 'var(--header-bg)', backdropFilter: 'blur(12px)', borderBottom: '1px solid var(--border)' }}
    >
      <div className="mx-auto max-w-6xl px-4 sm:px-6 py-4 flex items-center justify-between">
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
            {NAV_LINKS.map((l) => (
              <a key={l.href} href={l.href} className="nav-link">{l.label}</a>
            ))}
            <a href="https://github.com/redsandr/rag-variance-explainer" className="px-4 py-2 rounded-lg text-sm font-medium btn-primary">
              GitHub
            </a>
          </nav>

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
          <span className="text-sm font-semibold serif">Navigation</span>
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
              {l.label}
            </a>
          ))}
          <div className="mt-3 px-4">
            <a
              href="https://github.com/redsandr/rag-variance-explainer"
              onClick={closeMenu}
              className="block w-full text-center px-4 py-3 rounded-xl text-sm font-semibold btn-primary"
            >
              GitHub
            </a>
          </div>
        </div>
        <div className="px-5 py-4 flex items-center gap-3" style={{ borderTop: '1px solid var(--border)' }}>
          <Vernie pose="idle" size={24} />
          <span className="text-xs" style={{ color: 'var(--text-mute)' }}>MIT &middot; 2026</span>
        </div>
      </div>
    </header>
  );
}
