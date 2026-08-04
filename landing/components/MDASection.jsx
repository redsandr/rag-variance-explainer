import { MDA_CONTENT } from '../data/seo';

export default function MDASection() {
  const { title, subtitle, lede, sections } = MDA_CONTENT;

  return (
    <section id="mda" className="px-5 sm:px-7 py-24 md:py-28">
      <div className="w-full max-w-[860px] mx-auto">
        <div className="section-head">
          <span className="sec-num">03</span>
          <span className="sec-label">Key concept</span>
          <span className="sec-line"></span>
        </div>
        <h2 className="text-[clamp(2rem,5.4vw,4.2rem)] font-semibold tracking-[-0.035em] leading-[1.02] m-0 mb-3">{title}</h2>
        <p className="text-[clamp(1.02rem,1.8vw,1.2rem)] font-light leading-relaxed max-w-[62ch] mb-10" style={{ color: 'var(--text-dim)' }}>{subtitle}</p>

        <div className="seo-article">
          <p className="lede">{lede}</p>

          {sections.map((section, idx) => (
            <div key={idx} className="def-card">
              <div className="def-k">{section.heading}</div>
              <p>{section.content}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}