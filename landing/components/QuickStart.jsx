import { useState } from 'react';
import { CODE_SNIPPETS } from '../data/constants';

export default function QuickStart() {
  const [tab, setTab] = useState('local');
  const [copyLabel, setCopyLabel] = useState('Copy');

  function copyCode() {
    navigator.clipboard.writeText(CODE_SNIPPETS[tab]).then(() => {
      setCopyLabel('Copied');
      setTimeout(() => setCopyLabel('Copy'), 1500);
    });
  }

  return (
    <section className="max-w-4xl mx-auto px-4 sm:px-6 py-20 sm:py-24 md:py-32">
      <div className="mb-10 sm:mb-14">
        <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent)' }}>For engineers &amp; reviewers</div>
        <p className="serif text-2xl sm:text-3xl md:text-4xl font-bold">Running in two minutes.</p>
        <p className="text-sm sm:text-base mt-3" style={{ color: 'var(--text-dim)' }}>Want to run it yourself or see exactly how it works under the hood? Here&apos;s the full setup.</p>
      </div>
      <div className="rounded-2xl overflow-hidden card">
        <div className="flex flex-wrap items-center justify-between gap-y-2 gap-x-3 px-2 sm:px-4" style={{ borderBottom: '1px solid var(--border)' }}>
          <div className="flex flex-wrap">
            {['local', 'openai', 'claude'].map((t) => (
              <button
                key={t}
                className={`tab-btn px-3 sm:px-6 py-3 text-sm font-medium ${tab === t ? 'active' : ''}`}
                style={{ borderBottom: tab === t ? '2px solid var(--accent)' : '2px solid transparent' }}
                onClick={() => setTab(t)}
              >
                {t === 'local' ? 'Local model' : t === 'openai' ? 'OpenAI API' : 'Claude API'}
              </button>
            ))}
          </div>
          <button
            className="copy-btn flex items-center gap-1.5 mb-2 sm:mb-0 sm:mr-4 px-3 py-1.5 rounded-lg text-xs font-medium"
            style={{ border: '1px solid var(--border-strong)', color: 'var(--text-dim)' }}
            onClick={copyCode}
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="9" y="9" width="13" height="13" rx="2" />
              <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
            </svg>
            <span>{copyLabel}</span>
          </button>
        </div>
        <pre className="mono text-xs sm:text-sm p-4 sm:p-6 overflow-x-auto leading-relaxed" style={{ color: 'var(--text-dim)' }}>
          {CODE_SNIPPETS[tab]}
        </pre>
      </div>
    </section>
  );
}
