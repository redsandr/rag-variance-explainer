import Head from 'next/head';
import { motion, useReducedMotion } from 'framer-motion';
import ExampleWalkthrough from '../components/ExampleWalkthrough';
import SiteLayout, { ArrowIcon, repositoryUrl } from '../components/SiteLayout';

const questions = [
  { question: 'Can I ask my own question on this website?', answer: 'Not yet. This website walks through an illustrative research process. The open-source project runs locally; there is no public hosted analysis service here.' },
  { question: 'Does a matching quote prove the explanation?', answer: 'No. A quote check only tests whether words occur in a retrieved passage. The metric, period, arithmetic and causal language still need review in the original filing.' },
  { question: 'Why is there no example quotation?', answer: 'No filing-backed case has completed manual review for publication. Showing an invented SEC quotation would make the demonstration look more certain than the evidence allows.' },
  { question: 'What can I do now?', answer: 'Explore the interactive workpaper, read the method, or follow the local installation guide. You can also suggest a filing case through the public project repository.' },
];

export default function Home() {
  const reducedMotion = useReducedMotion();
  return <SiteLayout active="home">
    <Head>
      <title>Variance Explainer | Understand what changed in SEC filings</title>
      <meta name="description" content="Explore how an analyst can investigate changes in SEC 10-K and 10-Q filings, inspect the evidence and understand the limits of quote verification." />
    </Head>

    <section className="home-hero wrap" aria-labelledby="hero-title">
      <div className="home-hero-copy">
        <h1 id="hero-title">Understand what moved.<br /><span>See where it came from.</span></h1>
        <p>Investigate why a financial metric changed using passages from a company’s own SEC filings. Follow the source, check the quoted words, and decide what the disclosure actually supports.</p>
        <div className="home-hero-actions"><a className="primary-action" href="/example">Explore the example <ArrowIcon /></a><a className="secondary-action" href="/method">See how it works <ArrowIcon /></a></div>
        <p className="home-hero-context">SEC 10-K / 10-Q research <span aria-hidden="true">·</span> Local prototype <span aria-hidden="true">·</span> Not investment advice</p>
      </div>
      <motion.div className="home-preview" aria-label="Illustrative evidence workpaper with no published financial answer"
        initial={reducedMotion ? false : { opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.65, ease: [0.16, 1, 0.3, 1] }}>
        <div className="home-preview-top"><span>Variance / research note</span><span>Illustrative layout</span></div>
        <div className="home-preview-question"><span>Ask the filing</span><strong>Why did this metric change?</strong></div>
        <div className="home-preview-record"><span>01 / Proposed explanation</span><strong>Awaiting reviewed case</strong><p>No financial conclusion is published here without filing review.</p></div>
        <div className="home-preview-row"><span>02 / Exact passage</span><strong>Not published</strong></div>
        <div className="home-preview-row"><span>03 / Original filing</span><strong>Review pending</strong></div>
        <div className="home-preview-bottom"><span className="home-preview-pulse" aria-hidden="true" /> Evidence status is visible before any answer</div>
      </motion.div>
    </section>

    <section className="home-intro wrap" aria-labelledby="home-intro-title">
      <h2 id="home-intro-title">From a question to a source you can inspect.</h2>
      <p>Filings are dense. A plausible answer without its source is hard to audit. The prototype brings the relevant passage, proposed explanation and verification boundary into one research flow. It does not replace your own reading of the disclosure.</p>
    </section>

    <section className="home-example" id="example" aria-labelledby="home-example-title">
      <div className="wrap">
        <div className="section-heading"><div><h2 id="home-example-title">See how an answer earns its place.</h2><p>Choose a stage. Watch the workpaper change without pretending an unreviewed filing answer is real.</p></div><a className="text-link" href="/example">Open the full example <ArrowIcon /></a></div>
        <ExampleWalkthrough compact />
      </div>
    </section>

    <section className="home-outcomes wrap" id="how-it-works" aria-labelledby="home-outcomes-title">
      <div className="home-outcomes-lead"><h2 id="home-outcomes-title">What the analyst gets.</h2><p>Less time hunting through passages. More clarity about which part of an explanation is evidence and which part still needs judgment.</p></div>
      <div className="home-outcomes-list">
        <div><span>01</span><div><h3>A focused starting point.</h3><p>Relevant MD&A passages from the indexed filings, organized around the question you asked.</p></div></div>
        <div><span>02</span><div><h3>The words behind the answer.</h3><p>When a structured answer passes quote checking, the matched text is shown alongside its source passage.</p></div></div>
        <div><span>03</span><div><h3>A boundary you can see.</h3><p>A text match is labeled as a text match. Causation and arithmetic remain questions for filing review.</p></div></div>
      </div>
    </section>

    <section className="home-trust" id="trust" aria-labelledby="home-trust-title"><div className="wrap home-trust-inner"><div><h2 id="home-trust-title">A citation is a lead.<br /><span>Not a verdict.</span></h2><p>Research tools should make uncertainty legible, not hide it behind confident prose.</p></div><div className="home-trust-points"><div><strong>What the prototype checks</strong><p>Whether a generated quotation is present in its cited retrieved passage. If a required check fails, the answer is withheld as a sourced finding.</p></div><div><strong>What it does not establish</strong><p>That the quoted words prove the cause, that every driver was found, or that any calculation is correct. An analyst checks those against the original SEC document.</p></div><a href="/method">Read the method and limitations <ArrowIcon /></a></div></div></section>

    <section className="home-next wrap" aria-labelledby="home-next-title"><div><h2 id="home-next-title">Take the next step.</h2><p>Explore the research process here. Run the project locally when you want to inspect the implementation, or suggest a filing case to review.</p></div><div><a className="primary-action" href="/install">Install locally <ArrowIcon /></a><a className="secondary-action" href="/contact">Request a case <ArrowIcon /></a></div></section>

    <section className="home-faq wrap" id="faq" aria-labelledby="home-faq-title"><div className="section-heading"><div><h2 id="home-faq-title">Before you rely on it.</h2><p>Clear answers about what this site can and cannot demonstrate today.</p></div></div><div className="faq-list">{questions.map(({ question, answer }) => <details key={question}><summary>{question}<span aria-hidden="true">+</span></summary><p>{answer}</p></details>)}</div><p className="home-faq-foot"><a href={repositoryUrl} target="_blank" rel="noopener noreferrer">Inspect the open-source project <ArrowIcon diagonal /></a></p></section>
  </SiteLayout>;
}
