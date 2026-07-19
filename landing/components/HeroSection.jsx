import Vernie from './Vernie';
import HeroBackground from './HeroBackground';

export default function HeroSection() {
  return (
    <section className="relative flex items-center px-4 sm:px-6 pt-28 sm:pt-32 pb-10 sm:pb-24 overflow-hidden">
      <HeroBackground />
      <div className="mx-auto max-w-4xl w-full relative z-10 text-center">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-1.5 sm:gap-3 mb-5 sm:mb-6">
          <Vernie pose="waving" size={32} />
          <div
            className="inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-[10px] sm:text-xs font-medium text-center"
            style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}
          >
            <span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ background: 'var(--accent)' }}></span>
            7 companies &middot; 4 industries &middot; your data stays in-house
          </div>
        </div>
        <h1 className="serif text-2xl sm:text-5xl md:text-6xl font-bold leading-[1.1] tracking-tight mb-3 sm:mb-6" style={{ color: 'var(--text)' }}>
          Stop reading filings.
          <br />
          Start <span style={{ color: 'var(--accent)' }}>understanding variance.</span>
        </h1>
        <p className="text-sm sm:text-lg md:text-xl leading-relaxed mb-6 sm:mb-9 max-w-2xl mx-auto" style={{ color: 'var(--text-dim)' }}>
          Ask why the number moved — in plain English, with the exact page cited, every time.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-2 sm:gap-3">
          <a href="#demo" className="w-full sm:w-auto px-5 sm:px-6 py-3 sm:py-3.5 rounded-xl text-xs sm:text-sm font-semibold btn-primary text-center">
            Try a sample analysis
          </a>
          <a href="https://github.com/redsandr/rag-variance-explainer" className="w-full sm:w-auto px-5 sm:px-6 py-3 sm:py-3.5 rounded-xl text-xs sm:text-sm font-medium btn-secondary text-center">
            View on GitHub
          </a>
        </div>
      </div>
    </section>
  );
}
