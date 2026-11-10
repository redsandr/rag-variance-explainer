import Head from 'next/head';
import ExampleWalkthrough from '../components/ExampleWalkthrough';
import SiteLayout, { ArrowIcon } from '../components/SiteLayout';

export default function Example() {
  return <SiteLayout active="example">
    <Head><title>Interactive example | Variance Explainer</title><meta name="description" content="Explore an analyst-controlled research workpaper showing how a financial question leads to filing passages, quote checking and human review, without invented SEC evidence." /></Head>
    <section className="example-heading wrap" aria-labelledby="example-title"><h1 id="example-title">Follow the evidence, one decision at a time.</h1><p>Choose each stage to see what belongs in a filing-backed explanation. This is an illustrative workpaper, not a live query or a verified financial result.</p><div className="example-notice"><strong>No published filing case yet.</strong><span>Source quotations, page references and financial conclusions appear only after they have been checked against the original SEC filing.</span></div></section>
    <section className="example-main wrap" aria-label="Interactive example"><ExampleWalkthrough /></section>
    <section className="example-after wrap" aria-labelledby="example-after-title"><div><h2 id="example-after-title">What would make an answer publishable?</h2><p>A source passage must be retrieved, its quoted words must match, and an analyst must inspect the original disclosure for the metric, period and claimed cause. Only then can a case be presented as reviewed.</p></div><div><a className="secondary-action" href="/method">See the verification boundaries <ArrowIcon /></a><a className="text-link" href="/install">Run the prototype locally <ArrowIcon /></a></div></section>
  </SiteLayout>;
}
