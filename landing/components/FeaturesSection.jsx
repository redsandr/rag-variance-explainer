import { FEATURES } from '../data/constants';

export default function FeaturesSection() {
  return (
    <section id="features" className="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32">
      <div className="mb-10 sm:mb-14">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Why financial teams use it</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold">Built for accuracy, security, and trust.</p>
      </div>
      <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4">
        {FEATURES.map((f) => (
          <div key={f.t} className="rounded-xl p-5 sm:p-6 card card-hover">
            <h3 className="text-sm font-semibold mb-2">{f.t}</h3>
            <p className="text-xs sm:text-sm leading-relaxed" style={{ color: 'var(--text-dim)' }}>{f.d}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
