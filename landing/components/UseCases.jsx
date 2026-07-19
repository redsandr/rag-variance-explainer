import { USE_CASES } from '../data/constants';

export default function UseCases() {
  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32">
      <div className="mb-10 sm:mb-14">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>Use cases</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold">Real questions, real answers.</p>
      </div>

      <div className="rounded-2xl overflow-hidden card hidden md:block">
        <table className="w-full text-left text-sm">
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', background: 'var(--surface-alt)' }}>
              <th className="px-6 py-4 font-medium" style={{ color: 'var(--text-dim)' }}>Question</th>
              <th className="px-6 py-4 font-medium" style={{ color: 'var(--text-dim)' }}>Answer includes</th>
              <th className="px-6 py-4 font-medium" style={{ color: 'var(--text-dim)' }}>Source</th>
            </tr>
          </thead>
          <tbody>
            {USE_CASES.map((uc) => (
              <tr key={uc.q} style={{ borderBottom: '1px solid var(--border)' }} className="hover:brightness-95 transition-all">
                <td className="px-6 py-4 font-medium">{uc.q}</td>
                <td className="px-6 py-4" style={{ color: 'var(--text-dim)' }}>{uc.a}</td>
                <td className="px-6 py-4">
                  <span
                    className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
                    style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}
                  >
                    {uc.src}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="space-y-3 md:hidden">
        {USE_CASES.map((uc) => (
          <div key={uc.q} className="rounded-xl p-4 card">
            <div className="text-sm font-medium mb-2">{uc.q}</div>
            <div className="text-sm mb-3" style={{ color: 'var(--text-dim)' }}>{uc.a}</div>
            <span
              className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium"
              style={{ background: 'var(--accent-soft)', color: 'var(--accent-light)' }}
            >
              {uc.src}
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
