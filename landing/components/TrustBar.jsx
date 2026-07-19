import { TRUST_ITEMS } from '../data/constants';

export default function TrustBar() {
  return (
    <section className="px-4 sm:px-6 pb-20 md:pb-28">
      <div className="max-w-6xl mx-auto rounded-2xl card px-5 sm:px-6 md:px-10 py-6 md:py-7">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-y-4 gap-x-4 sm:gap-x-6">
          {TRUST_ITEMS.map((item) => (
            <div key={item} className="flex items-center gap-2.5">
              <span
                className="flex items-center justify-center h-5 w-5 rounded-full shrink-0"
                style={{ background: 'var(--accent-soft)', color: 'var(--accent)' }}
              >
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M5 13l4 4L19 7" />
                </svg>
              </span>
              <span className="text-xs sm:text-sm font-medium leading-tight" style={{ color: 'var(--text-dim)' }}>{item}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
