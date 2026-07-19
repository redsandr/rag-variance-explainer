export default function ProblemSection() {
  return (
    <section className="max-w-4xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32 text-center">
      <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>The problem</div>
      <p className="serif text-xl sm:text-2xl md:text-3xl font-semibold leading-tight mb-6 mx-auto max-w-3xl">
        Financial analysts spend hours reading MD&amp;A sections every quarter.
      </p>
      <p className="text-sm sm:text-base leading-relaxed max-w-2xl mx-auto" style={{ color: 'var(--text-dim)' }}>
        Scanning tables, cross-referencing periods, hunting for the one sentence that explains why a number moved
        — it&apos;s manual, repetitive, and easy to get wrong under deadline pressure. This tool answers those
        questions directly from the filing text, with the source cited every time.
        <span style={{ color: 'var(--text)', fontWeight: 500 }}>
          {' '}It was built and tested to work the same way across four different industries — restaurant,
          retail, healthcare, energy — not just tuned to look good on one company.
        </span>
      </p>
    </section>
  );
}
