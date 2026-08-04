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
    <section className="px-5 sm:px-7 py-24 md:py-28">
      <div className="w-full max-w-[860px] mx-auto">
        <div className="section-head">
          <span className="sec-num">11</span>
          <span className="sec-label">Quick start</span>
          <span className="sec-line"></span>
        </div>
        <h2 className="text-[clamp(2rem,5.4vw,4.2rem)] font-semibold tracking-[-0.035em] leading-[1.02] m-0 mb-3">Running in two minutes.</h2>
        <p className="text-[15px] leading-relaxed mb-8 max-w-[58ch]" style={{ color: 'var(--text-dim)' }}>
          Want to run it yourself or see exactly how it works under the hood? Here&apos;s the full setup.
        </p>

        <div className="term">
          <div className="flex flex-wrap items-center justify-between gap-y-2 gap-x-3" style={{ borderBottom: '1px solid var(--border)' }}>
            <div className="flex flex-wrap px-2">
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
          <pre className="mono text-xs sm:text-sm p-5 sm:p-7 overflow-x-auto leading-relaxed" style={{ color: 'var(--text-dim)' }}>
            {CODE_SNIPPETS[tab]}
          </pre>
        </div>
      </div>
    </section>
  );
}