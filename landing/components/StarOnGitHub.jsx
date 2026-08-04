export default function StarOnGitHub() {
  return (
    <section className="px-5 sm:px-7 py-16 sm:py-20">
      <div className="w-full max-w-[860px] mx-auto text-center">
        <div className="rounded-2xl p-8 sm:p-12" style={{ background: 'var(--bg-soft)', border: '1.5px solid var(--accent)' }}>
          <p className="text-[clamp(1.6rem,4vw,2.4rem)] font-semibold tracking-[-0.03em] m-0 mb-3">Like what you see?</p>
          <p className="text-sm sm:text-base mb-8 max-w-md mx-auto leading-relaxed" style={{ color: 'var(--text-dim)' }}>
            If this project helped you, consider starring it on GitHub. It helps others find it too.
          </p>
          <a
            href="https://github.com/redsandr/rag-variance-explainer"
            className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl text-sm font-semibold btn-gold"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
            </svg>
            Star on GitHub
          </a>
        </div>
      </div>
    </section>
  );
}