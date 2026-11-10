import Head from 'next/head';
import SiteLayout from '../components/SiteLayout';

const stages = [
  { title: 'Collect the disclosure', detail: 'The index builder downloads selected SEC 10-K and 10-Q filings, extracts MD&A text, and splits it into passages. The index is not a parser for every table, footnote, or page of a filing.' },
  { title: 'Find relevant passages', detail: 'A question searches the local Chroma index. Dense retrieval, a BM25 merge, and cross-encoder reranking select passages for the model to read.' },
  { title: 'Draft a structured answer', detail: 'The configured LLM proposes claims with source indices and quotes. It may still confuse a metric or period, omit a driver, or infer a cause the filing does not state.' },
  { title: 'Check the quotation', detail: 'The verifier parses the answer and checks each quoted excerpt against its referenced retrieved passage, allowing case and whitespace differences. A parse failure or quote mismatch produces a refusal, not a sourced answer.' },
  { title: 'Read the original filing', detail: 'The analyst checks the original SEC filing for the exact metric, period, calculation, context, and management’s causal language before using a finding.' },
];

export default function Method() {
  return <SiteLayout active="method">
    <Head><title>Method | Variance Explainer</title><meta name="description" content="How the local variance research prototype retrieves SEC MD&A passages, checks quotes, and handles evidence limits." /></Head>
    <div className="secondary-page">
      <header className="secondary-hero wrap">
        <div><h1>Trace an explanation back to the disclosure.</h1><p className="secondary-lead">A useful variance answer starts with a relevant passage, not a plausible story. This is the path from a question to a source an analyst can inspect.</p><a className="secondary-text-link" href="/install">Run the local prototype <span aria-hidden="true">↗</span></a></div>
        <aside className="secondary-aside" aria-label="Evidence boundary"><span className="secondary-aside-label">Evidence boundary</span><p>A quote match means the words appear in a retrieved passage. It does not independently prove a cause, a calculation, or completeness.</p></aside>
      </header>

      <section className="secondary-section wrap" aria-labelledby="method-path-title"><div className="secondary-section-head"><h2 id="method-path-title">From filing to review</h2><p>Each stage narrows a question. None removes the need to read the filing.</p></div><ol className="method-path">{stages.map(({ title, detail }) => <li key={title}><h3>{title}</h3><p>{detail}</p></li>)}</ol></section>

      <section className="secondary-band" aria-labelledby="method-check-title"><div className="wrap secondary-band-grid"><div><h2 id="method-check-title">What the check can establish.</h2><p>Structured output and source-index checks help prevent an unmatched quotation from being presented as cited evidence.</p></div><div><h3>What it cannot establish.</h3><p>Matching text is not an independent audit of a company’s explanation. The verifier does not validate numerical arithmetic, causal truth, the full filing, or whether all relevant drivers were retrieved. Optional NLI is off by default pending independent evaluation.</p><p>Older indexed passages may lack an original SEC filing link. When a link is unavailable, the source must be located and checked separately.</p></div></div></section>

      <section className="secondary-section wrap" aria-labelledby="method-gates-title"><div className="secondary-section-head"><h2 id="method-gates-title">What remains before release</h2><p>These are open gates, not features already delivered.</p></div><div className="secondary-columns"><div><h3>Evidence</h3><ul className="secondary-list"><li>Build a small fresh index with filing URLs and check a complete answer against its original filing.</li><li>Review causal and numerical claims with a versioned, human-labeled question set.</li><li>Document failure cases, unsupported conclusions, and refusal behavior.</li></ul></div><div><h3>Operation</h3><ul className="secondary-list"><li>Repeat clean-clone installation and index checks across supported environments.</li><li>Validate UI, REST API, and MCP answers against reviewed cases.</li><li>Add authentication, resource limits, and security controls before any hosted service.</li></ul></div></div><div className="secondary-note">Today this is a local, single-user research prototype, not a production-ready or hosted analysis service. A local GGUF or local model server can keep model inference on your machine; optional OpenAI and Anthropic backends send retrieved passages to their APIs.</div></section>
      <section className="secondary-close wrap" aria-labelledby="method-next-title"><h2 id="method-next-title">Inspect the method in code.</h2><p>Start with the setup guide, then follow the index, retrieval, answer, and verifier modules in the repository.</p><div className="secondary-actions"><a className="secondary-button" href="/install">Installation guide <span aria-hidden="true">→</span></a><a className="secondary-text-link" href="https://github.com/redsandr/rag-variance-explainer" target="_blank" rel="noopener noreferrer">View repository <span aria-hidden="true">↗</span></a></div></section>
    </div>
  </SiteLayout>;
}
