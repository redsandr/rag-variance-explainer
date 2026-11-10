import Head from 'next/head';
import SiteLayout from '../components/SiteLayout';

const issueUrl = 'https://github.com/redsandr/rag-variance-explainer/issues/new';

export default function Contact() {
  return <SiteLayout active="contact">
    <Head><title>Request a case | Variance Explainer</title><meta name="description" content="Suggest a public SEC filing and an analyst question through the project's public GitHub issues." /></Head>
    <div className="secondary-page">
      <header className="secondary-hero wrap"><div><h1>Have a filing question worth examining?</h1><p className="secondary-lead">Suggest a public SEC filing and the metric you want to investigate. The project uses public GitHub issues for case requests and feedback, not a private contact form.</p><a className="secondary-button secondary-hero-button" href={issueUrl} target="_blank" rel="noopener noreferrer">Open a public GitHub issue <span aria-hidden="true">↗</span></a></div><aside className="secondary-aside" aria-label="Before submitting"><span className="secondary-aside-label">Before submitting</span><p>Issues are public. Do not include personal information, confidential research, private documents, or credentials.</p></aside></header>
      <section className="secondary-section wrap" aria-labelledby="contact-useful-title"><div className="secondary-section-head"><h2 id="contact-useful-title">What makes a useful request?</h2><p>Enough context to locate the disclosure without sharing private material.</p></div><ul className="contact-prompt-list"><li><h3>Identify the filing.</h3><p>Give the company, SEC form, reporting period, and a link to the public filing if you have one.</p></li><li><h3>Name the change.</h3><p>Say which metric and periods you want to compare. Keep the question specific without supplying a presumed answer.</p></li><li><h3>Explain the uncertainty.</h3><p>Note which management statement or competing interpretation you want checked against the original filing.</p></li></ul></section>
      <section className="secondary-band" aria-labelledby="contact-expect-title"><div className="wrap secondary-band-grid"><div><h2 id="contact-expect-title">A request is not an approved result.</h2></div><div><p>Submitting an issue does not generate an analysis, reserve demo access, or guarantee a response. A case will not be published as verified unless its evidence has been reviewed against the original SEC filing.</p><a className="secondary-text-link" href="/method">See the review boundary <span aria-hidden="true">→</span></a></div></div></section>
      <section className="secondary-close wrap" aria-labelledby="contact-next-title"><h2 id="contact-next-title">Ready to share the question?</h2><p>GitHub may ask you to sign in before you create a public issue.</p><a className="secondary-button" href={issueUrl} target="_blank" rel="noopener noreferrer">Request a case on GitHub <span aria-hidden="true">↗</span></a></section>
    </div>
  </SiteLayout>;
}
