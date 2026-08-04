import HeroBackground from './HeroBackground';

export default function HeroSection() {
  return (
    <section id="top" className="relative flex flex-col items-center px-5 sm:px-7 pt-28 sm:pt-36 pb-16 overflow-hidden">
      <div className="ghost-outline" aria-hidden="true">Variance explained</div>
      <HeroBackground />
      <div className="w-full max-w-[1180px] relative z-10">
        <div className="eyebrow">
          <span className="dot"></span>
          <span><b>AI Financial Variance Analysis from SEC Filings</b></span>
        </div>
        <h1 className="hero-title">
          Ask why <span className="gold-text">revenue, margin,<br />labor cost</span> changed.
        </h1>
        <p className="hero-sub">
          Get grounded answers with page-level citations from SEC 10-K and 10-Q filings in seconds.
          Stop searching PDFs. Start explaining variance.
        </p>
        <div className="hero-cta">
          <a href="#demo" className="btn btn-gold">Try a sample analysis</a>
          <a href="https://github.com/redsandr/rag-variance-explainer" className="btn btn-ghost">
            View on GitHub <span className="arr">↗</span>
          </a>
        </div>
        <div className="hero-trust">
          <div className="trust-item"><span>Grounded in <b>SEC filings</b></span></div>
          <div className="trust-item"><span>Every answer <b>cited</b></span></div>
          <div className="trust-item"><span>Runs <b>fully offline</b></span></div>
          <div className="trust-item"><span><b>7</b> companies</span></div>
          <div className="trust-item"><span><b>4</b> industries</span></div>
        </div>
      </div>
    </section>
  );
}