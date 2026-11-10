import Head from 'next/head';
import SiteLayout, { ArrowIcon } from '../components/SiteLayout';

export default function Custom404() {
  return (
    <SiteLayout>
      <Head><title>Page not found | Variance Explainer</title></Head>
      <section className="wrap not-found"><h1>Page not found.</h1><p>This address does not point to a page in the research prototype.</p><a className="primary-action" href="/">Return to the homepage <ArrowIcon /></a></section>
    </SiteLayout>
  );
}
