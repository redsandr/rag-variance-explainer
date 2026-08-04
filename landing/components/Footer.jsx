export default function Footer() {
  return (
    <footer style={{ borderTop: '1px solid var(--border)' }}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-7 py-14">
        <div className="flex flex-wrap justify-between gap-10 pb-10">
          <div className="max-w-[320px]">
            <a href="#top" className="flex items-center gap-2.5 font-semibold tracking-tight">
              <span className="w-[26px] h-[26px] rounded-lg flex items-center justify-center shrink-0" style={{ background: 'var(--gold-grad)' }}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#08080d" strokeWidth="2.5">
                  <path d="M12 2 L22 8 L22 16 L12 22 L2 16 L2 8 Z" />
                </svg>
              </span>
              Variance Explainer
            </a>
            <p className="text-sm font-light leading-relaxed mt-3" style={{ color: 'var(--text-mute)' }}>
              A grounded RAG pipeline over real SEC filings - plain-English answers cited to the exact page.
              Runs fully on-device, no API keys needed.
            </p>
          </div>
          <div className="flex gap-14 flex-wrap">
            <div>
              <h5 className="mono text-[11px] tracking-[0.22em] uppercase m-0 mb-4" style={{ color: 'var(--text-mute)' }}>Explore</h5>
              <a href="#demo" className="block text-sm mb-2.5 transition-colors" style={{ color: 'var(--text-dim)' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--accent-bright)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>Live demo</a>
              <a href="#evidence" className="block text-sm mb-2.5 transition-colors" style={{ color: 'var(--text-dim)' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--accent-bright)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>Evidence</a>
              <a href="#how" className="block text-sm mb-2.5 transition-colors" style={{ color: 'var(--text-dim)' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--accent-bright)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>How it works</a>
              <a href="#roadmap" className="block text-sm transition-colors" style={{ color: 'var(--text-dim)' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--accent-bright)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>Roadmap</a>
            </div>
            <div>
              <h5 className="mono text-[11px] tracking-[0.22em] uppercase m-0 mb-4" style={{ color: 'var(--text-mute)' }}>Project</h5>
              <a href="https://github.com/redsandr/rag-variance-explainer" className="block text-sm mb-2.5 transition-colors" style={{ color: 'var(--text-dim)' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--accent-bright)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>GitHub</a>
              <a href="https://medium.com/p/f769687defe9" className="block text-sm mb-2.5 transition-colors" style={{ color: 'var(--text-dim)' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--accent-bright)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>Blog post</a>
              <a href="#" className="block text-sm transition-colors" style={{ color: 'var(--text-dim)' }} onMouseEnter={(e)=>{e.currentTarget.style.color='var(--accent-bright)'}} onMouseLeave={(e)=>{e.currentTarget.style.color='var(--text-dim)'}}>MIT license</a>
            </div>
          </div>
        </div>
        <div className="mt-7 flex flex-wrap justify-between gap-2 mono text-[11.5px]" style={{ color: 'var(--text-mute)' }}>
          <span>Variance Explainer</span>
          <span>Open source &middot; MIT &middot; 2026</span>
        </div>
      </div>
    </footer>
  );
}