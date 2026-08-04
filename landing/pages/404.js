import Head from 'next/head';

export default function Custom404() {
  return (
    <div className="antialiased bg-mesh min-h-screen flex items-center justify-center px-6">
      <Head>
        <title>Page not found - RAG Variance Explainer</title>
      </Head>
      <div className="text-center max-w-md">
        <p className="mono text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: 'var(--accent-bright)' }}>
          404 / Not found
        </p>
        <h1 className="text-[clamp(2rem,6vw,3rem)] font-semibold tracking-[-0.03em] mb-4" style={{ color: 'var(--text)' }}>
          Couldn&apos;t find that filing&hellip;
        </h1>
        <p className="text-base leading-relaxed mb-9" style={{ color: 'var(--text-dim)' }}>
          The page you&apos;re looking for may have moved, or never existed in the first place.
        </p>
        <div className="flex items-center justify-center gap-3">
          <a href="/" className="px-5 py-3 rounded-xl text-sm font-semibold btn-primary">
            Back to home
          </a>
          <a
            href="https://github.com/redsandr/rag-variance-explainer"
            className="px-5 py-3 rounded-xl text-sm font-medium btn-secondary"
          >
            View on GitHub
          </a>
        </div>
      </div>
    </div>
  );
}