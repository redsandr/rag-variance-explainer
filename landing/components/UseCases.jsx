import { USE_CASES } from '../data/constants';

const SPANS = ['lg:col-span-8', 'lg:col-span-4', 'lg:col-span-4', 'lg:col-span-4', 'lg:col-span-4'];

export default function UseCases() {
  return (
    <section className="px-5 sm:px-7 py-24 md:py-28">
      <div className="w-full max-w-[1180px] mx-auto">
        <div className="section-head">
          <span className="sec-num">09</span>
          <span className="sec-label">Financial Variance Analysis Examples</span>
          <span className="sec-line"></span>
        </div>
        <h2 className="text-[clamp(2rem,5.4vw,4.2rem)] font-semibold tracking-[-0.035em] leading-[1.02] m-0 mb-10">Real questions, real answers.</h2>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {USE_CASES.map((uc, i) => (
            <div
              key={uc.q}
              className={`flex flex-col justify-between min-h-[190px] p-6 rounded-2xl ${SPANS[i % SPANS.length]}`}
              style={{ background: 'var(--bg-soft)', border: '1px solid var(--border)', transition: 'border-color 0.2s, transform 0.2s' }}
              onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--accent)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.transform = 'translateY(0)'; }}
            >
              <div className="text-[17px] font-semibold tracking-[-0.01em] leading-snug">{uc.q}</div>
              <div>
                <div className="mt-auto pt-4 text-[13.5px] leading-relaxed" style={{ color: 'var(--text-dim)' }}>{uc.a}</div>
                <div className="mt-3.5 mono text-[10.5px] tracking-[0.05em]" style={{ color: 'var(--accent)' }}>{uc.src}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}