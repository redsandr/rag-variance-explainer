import { useState } from 'react';

const environments = {
  windows: { label: 'Windows', commands: 'py -3.11 -m venv .venv\n.\\.venv\\Scripts\\Activate.ps1\npython -m pip install -e .\nCopy-Item .env.example .env' },
  unix: { label: 'macOS / Linux', commands: 'python3.11 -m venv .venv\nsource .venv/bin/activate\npython -m pip install -e .\ncp .env.example .env' },
};

export default function SetupGuide({ repository }) {
  const [platform, setPlatform] = useState('windows');
  const [copyState, setCopyState] = useState('Copy commands');
  const selected = environments[platform];

  async function copyCommands() {
    try {
      await navigator.clipboard.writeText(selected.commands);
      setCopyState('Copied');
    } catch {
      setCopyState('Select and copy the commands');
    }
  }

  function selectPlatform(key) {
    setPlatform(key);
    setCopyState('Copy commands');
  }

  return <section className="setup wrap" id="setup" aria-labelledby="setup-title"><div className="setup-heading"><div><h2 id="setup-title">Run the research locally.</h2><p>Inspect the code, build your own index and verify every answer against its filing. There is no hosted analysis service to install from this page.</p></div><a href={`${repository}#run-locally`} target="_blank" rel="noopener noreferrer">Read the full setup guide ↗</a></div><div className="setup-grid"><div className="setup-steps"><div><span>01</span><h3>Prepare your environment.</h3><p>Use Python 3.11. Install the base package, then choose a local GGUF model or an API backend as described in the README.</p></div><div><span>02</span><h3>Identify yourself to SEC.</h3><p>Set <code>SEC_USER_AGENT</code> in <code>.env</code> to your name and contact email before requesting filings.</p></div><div><span>03</span><h3>Build, then inspect.</h3><p>Run <code>python src/build_index.py</code>, then <code>streamlit run app.py</code>. First-time downloads and indexing can take substantial time.</p></div></div><div className="setup-code"><div className="setup-code-top"><div className="setup-tabs" aria-label="Installation platform">{Object.entries(environments).map(([key, value]) => <button type="button" key={key} aria-pressed={platform === key} className={platform === key ? 'is-active' : ''} onClick={() => selectPlatform(key)}>{value.label}</button>)}</div><button type="button" className="copy-commands" onClick={copyCommands} aria-live="polite">{copyState}</button></div><pre><code>{selected.commands}</code></pre><div className="setup-code-foot">Run from the cloned repository root. Configure a model backend before building the index.</div></div></div></section>;
}
