import Head from 'next/head';
import Vernie from '../components/Vernie';

export default function Custom404() {
  return (
    <div className="antialiased bg-mesh min-h-screen flex items-center justify-center px-6">
      <Head>
        <title>Page not found &mdash; RAG Variance Explainer</title>
      </Head>
      <div className="text-center max-w-md">
        <div className="flex justify-center mb-8">
          <Vernie pose="confused" size={80} />
        </div>
        <p
          className="text-xs font-semibold uppercase tracking-widest mb-4"
          style={{ color: 'var(--accent)' }}
        >
          404
        </p>
        <h1 className="serif text-3xl md:text-4xl font-bold mb-4" style={{ color: 'var(--text)' }}>
          Couldn&apos;t find that filing&hellip;
        </h1>
        <p className="text-base leading-relaxed mb-9" style={{ color: 'var(--text-dim)' }}>
          Vernie searched every page and came up empty. The page you&apos;re looking for may have moved,
          or never existed in the first place.
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
