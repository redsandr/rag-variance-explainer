import Head from 'next/head';

export default function Custom404() {
  return (
    <div className="site-shell">
      <Head><title>Page not found | Variance Explainer</title></Head>
      <header className="site-header wrap"><a className="brand" href="/"><span className="brand-mark" aria-hidden="true"><span></span><span></span></span><span>Variance Explainer</span></a></header>
      <main className="wrap not-found"><h1>Page not found.</h1><p>This address does not point to a page in the research prototype.</p><a className="primary-action" href="/">Return to the homepage <span aria-hidden="true">→</span></a></main>
    </div>
  );
}
