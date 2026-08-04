export default function ProblemSection() {
  return (
    <section className="px-5 sm:px-7 py-24 md:py-32">
      <div className="w-full max-w-[1180px] mx-auto">
        <div className="section-head">
          <span className="sec-num">02</span>
          <span className="sec-label">The problem</span>
          <span className="sec-line"></span>
        </div>

        <div className="grid md:grid-cols-[1.1fr_0.9fr] gap-12 md:gap-16 items-start">
          <div>
            <h2 className="text-[clamp(2rem,5.4vw,4.2rem)] font-semibold tracking-[-0.035em] leading-[1.02] m-0 mb-5">
              Why Financial Metrics <span className="gold-text">Changed</span>
            </h2>
            <p className="text-[clamp(1.02rem,1.8vw,1.2rem)] font-light leading-relaxed max-w-[60ch] m-0" style={{ color: 'var(--text-dim)' }}>
              Financial variance analysis often requires analysts to manually search SEC 10-K and 10-Q
              filings, read Management Discussion & Analysis (MD&A), and connect changes in
              financial metrics to the underlying business drivers. Slow, error-prone - and it doesn&apos;t
              scale across 7 companies and 4 industries.
            </p>
          </div>
          <div>
            <div className="stat-gold">4&nbsp;hrs&nbsp;&rarr;&nbsp;3&nbsp;min</div>
            <ul className="meh-list">
              <li><b>The manual crawl</b><span>Open the filing, search the filer, find the number, read the MD&A context.</span></li>
              <li><b>The trust gap</b><span>No guarantee the paragraph you landed on is the one that moved the metric.</span></li>
              <li><b>The scale wall</b><span>Do this across a basket of companies and the process breaks down completely.</span></li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}