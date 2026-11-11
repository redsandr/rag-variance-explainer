import Head from 'next/head';
import ExampleWalkthrough from '../components/ExampleWalkthrough';
import SiteLayout, { ArrowIcon } from '../components/SiteLayout';

export default function Example() {
  return <SiteLayout active="example">
    <Head><title>JNJ Europe sales case | Variance Explainer</title><meta name="description" content="Explore a reviewed, static JNJ Europe sales case with the original SEC filing and the limits of quote matching. No live model runs on this website." /></Head>
    <section className="example-heading wrap" aria-labelledby="example-title"><h1 id="example-title">Follow one change back to the filing.</h1><p>Explore a locally generated J&J Europe sales finding, checked against the original SEC 10-Q. Choose each stage to inspect the evidence. This website does not run live analysis.</p><div className="example-notice"><strong>Reviewed case · static walkthrough.</strong><span>The reported growth breakdown was checked against the filing body; this does not certify other model answers.</span></div></section>
    <section className="example-main wrap" aria-label="Interactive example"><ExampleWalkthrough /></section>
    <section className="example-after wrap" aria-labelledby="example-after-title"><div><h2 id="example-after-title">What can this tell you?</h2><p>The filing reports a regional growth breakdown, not every underlying business driver. Matching a quotation in retrieved text cannot establish arithmetic, causation, or completeness for other answers. This is not investment advice.</p></div><div><a className="secondary-action" href="/method">See the verification boundaries <ArrowIcon /></a><a className="text-link" href="/install">Run the prototype locally <ArrowIcon /></a></div></section>
  </SiteLayout>;
}
