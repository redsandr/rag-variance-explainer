import { ROADMAP } from '../data/constants';

export default function RoadmapSection() {
  return (
    <section className="max-w-4xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32">
      <div className="mb-10 sm:mb-14">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Roadmap</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold">What&apos;s next.</p>
      </div>
      <div className="grid gap-3">
        {ROADMAP.map((item) => (
          <div key={item} className="flex items-center gap-4 px-5 sm:px-6 py-4 rounded-xl card card-hover">
            <span className="h-1.5 w-1.5 rounded-full shrink-0" style={{ background: 'var(--accent)' }}></span>
            <span className="text-sm" style={{ color: 'var(--text-dim)' }}>{item}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
