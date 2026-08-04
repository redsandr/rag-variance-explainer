import { FEATURES } from '../data/constants';

export default function FeaturesSection() {
  return (
    <section id="features" className="px-5 sm:px-7 py-24 md:py-28">
      <div className="w-full max-w-[860px] mx-auto">
        <div className="section-head">
          <span className="sec-num">10</span>
          <span className="sec-label">Why Financial Analysts Use It</span>
          <span className="sec-line"></span>
        </div>
        <ul className="feat-list">
          {FEATURES.map((f, i) => (
            <li key={f.t}>
              <span className="feat-n">{String(i + 1).padStart(2, '0')}</span>
              <div>
                <h4 className="m-0 mb-2 text-[22px] font-semibold tracking-[-0.02em]">{f.t}</h4>
                <p className="m-0 text-[15px] leading-relaxed max-w-[58ch]" style={{ color: 'var(--text-dim)' }}>{f.d}</p>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}