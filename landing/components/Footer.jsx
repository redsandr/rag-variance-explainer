import Vernie from './Vernie';

export default function Footer() {
  return (
    <footer style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-3 text-sm" style={{ color: 'var(--text-mute)' }}>
          <Vernie pose="idle" size={32} />
          <span>MIT License</span>
          <span className="hidden sm:inline">&middot;</span>
          <span>2026</span>
        </div>
        <div className="flex items-center gap-4 sm:gap-6 text-sm">
          <a href="#how" className="nav-link">Methodology</a>
          <a href="https://github.com/redsandr/rag-variance-explainer" className="nav-link">GitHub</a>
          <a href="https://github.com/redsandr/rag-variance-explainer/tree/master/docs" className="nav-link">Docs</a>
        </div>
      </div>
    </footer>
  );
}
