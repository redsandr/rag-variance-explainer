import { useState } from 'react';
import Head from 'next/head';
import SiteLayout from '../components/SiteLayout';

const environments = {
  windows: { label: 'Windows PowerShell', commands: 'py -3.11 -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npython -m pip install -e .\nCopy-Item .env.example .env' },
  unix: { label: 'macOS / Linux', commands: 'python3.11 -m venv .venv\nsource .venv/bin/activate\npython -m pip install -e .\ncp .env.example .env' },
};

export default function Install() {
  const [platform, setPlatform] = useState('windows');
  const [copyStatus, setCopyStatus] = useState('');
  const selected = environments[platform];

  async function copyCommands() {
    try {
      await navigator.clipboard.writeText(selected.commands);
      setCopyStatus(`${selected.label} commands copied.`);
    } catch {
      setCopyStatus('Copy unavailable. Select the commands below to copy them manually.');
    }
  }

  function selectPlatform(key) {
    setPlatform(key);
    setCopyStatus('');
  }

  return <SiteLayout active="install">
    <Head><title>Install locally | Variance Explainer</title><meta name="description" content="Run the SEC filing research prototype locally with Python 3.11, a configured model backend, and an SEC user agent." /></Head>
    <div className="secondary-page">
      <header className="secondary-hero wrap"><div><h1>Run your own research environment.</h1><p className="secondary-lead">Clone the open-source repository, configure a model, and build an index on your machine. This site does not host the analysis tool or supply a prebuilt index.</p><a className="secondary-text-link" href="https://github.com/redsandr/rag-variance-explainer" target="_blank" rel="noopener noreferrer">Open repository <span aria-hidden="true">↗</span></a></div><aside className="secondary-aside" aria-label="Before you begin"><span className="secondary-aside-label">Before you begin</span><p>Python 3.11, enough disk space for downloads and an index, and internet access for SEC filings and embedding models. An LLM backend is configured separately.</p></aside></header>

      <section className="secondary-section wrap" aria-labelledby="install-environment-title"><div className="secondary-section-head"><h2 id="install-environment-title">Create the environment</h2><p>Run these commands from the cloned repository root. The tabs change only the shell commands, not the other prerequisites.</p></div><div className="install-terminal"><div className="install-toolbar"><div className="install-tabs" role="group" aria-label="Choose your operating system">{Object.entries(environments).map(([key, value]) => <button key={key} type="button" aria-pressed={platform === key} className={platform === key ? 'is-selected' : ''} onClick={() => selectPlatform(key)}>{value.label}</button>)}</div><button className="install-copy" type="button" onClick={copyCommands}>Copy commands</button></div><pre aria-label={`${selected.label} setup commands`}><code>{selected.commands}</code></pre></div><p className="install-feedback" role="status" aria-live="polite">{copyStatus}</p><p className="secondary-small">On Windows, check <code>py -0p</code> first. If Python 3.11 is not listed, install it or use its executable directly. See the <a href="https://github.com/redsandr/rag-variance-explainer#run-locally" target="_blank" rel="noopener noreferrer">full README setup guide</a>.</p></section>

      <section className="secondary-band" aria-labelledby="install-config-title"><div className="wrap secondary-band-grid"><div><h2 id="install-config-title">Configure before indexing.</h2><p>The environment commands install the base package. They do not provide a model or identify you to the SEC.</p></div><div><h3>Identify your SEC requests</h3><p>In <code>.env</code>, set <code>SEC_USER_AGENT</code> to your name and contact email. SEC requests fail when it is missing.</p><h3>Choose a model backend</h3><p>For local GGUF inference, install <code>python -m pip install -e &quot;.[local]&quot;</code>, supply a compatible model, and set <code>LLAMA_CPP_MODEL_PATH</code>. A local llama.cpp server is another option. OpenAI and Anthropic backends are optional; they send retrieved filing passages to an external API and can incur charges. Follow the README for backend-specific configuration.</p></div></div></section>

      <section className="secondary-section wrap" aria-labelledby="install-run-title"><div className="secondary-section-head"><h2 id="install-run-title">Build, then open the UI</h2><p>After configuring <code>.env</code> and the backend, run these from the repository root.</p></div><pre className="install-run-code"><code>python src/build_index.py{'\n'}streamlit run app.py</code></pre><div className="secondary-columns"><p>The first build downloads filings and models and may take substantial time. A checkpoint allows a failed or interrupted index build to resume after you fix the cause.</p><p>Review original filings before relying on an answer. A quote match checks retrieved text, not a causal conclusion or calculation.</p></div></section>
      <section className="secondary-close wrap" aria-labelledby="install-next-title"><h2 id="install-next-title">Want the evidence boundary first?</h2><p>Read how passages are selected, checked, and withheld when validation fails.</p><div className="secondary-actions"><a className="secondary-button" href="/method">Read the method <span aria-hidden="true">→</span></a><a className="secondary-text-link" href="https://github.com/redsandr/rag-variance-explainer#run-locally" target="_blank" rel="noopener noreferrer">Full setup in README <span aria-hidden="true">↗</span></a></div></section>
    </div>
  </SiteLayout>;
}
