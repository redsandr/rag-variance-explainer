import Vernie from './Vernie';

export default function StarOnGitHub() {
  return (
    <section className="max-w-4xl mx-auto px-4 sm:px-6 py-16 sm:py-20 text-center">
      <div className="rounded-2xl card p-8 sm:p-10 md:p-12" style={{ borderColor: 'var(--accent)', borderWidth: '1.5px' }}>
        <div className="flex justify-center mb-5">
          <Vernie pose="waving" size={56} />
        </div>
        <p className="serif text-2xl sm:text-3xl font-bold mb-3">Like what you see?</p>
        <p className="text-sm sm:text-base mb-7 max-w-md mx-auto" style={{ color: 'var(--text-dim)' }}>
          If this project helped you, consider starring it on GitHub. It helps others find it too.
        </p>
        <a
          href="https://github.com/redsandr/rag-variance-explainer"
          className="inline-flex items-center gap-2.5 px-6 py-3.5 rounded-xl text-sm font-semibold btn-primary"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          Star on GitHub
        </a>
      </div>
    </section>
  );
}
