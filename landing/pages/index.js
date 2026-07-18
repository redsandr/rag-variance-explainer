import Head from 'next/head'

const companies = ['CMG', 'DRI', 'CBRL', 'WMT', 'TGT', 'JNJ', 'XOM']
const sectors = ['Restaurant', 'Retail', 'Healthcare', 'Energy']

const useCases = [
  { q: 'Why did Chipotle\'s labor costs change?', a: 'Wage inflation, CA minimum wage, sales leverage', src: 'CMG 10-K/10-Q' },
  { q: 'What drove Walmart\'s e-commerce growth?', a: 'Omnichannel penetration, store-fulfilled pickup/delivery', src: 'WMT 10-K/10-Q' },
  { q: 'How did Target\'s gross margin rate change?', a: 'Merchandise mix, promotions, shrink impact', src: 'TGT 10-K/10-Q' },
  { q: 'How did Darden\'s acquisition of Chuy\'s impact revenue?', a: 'Purchase price, sales contribution, segment profit', src: 'DRI 10-K/10-Q' },
  { q: 'How do WMT and TGT compare on inventory turnover?', a: 'Cross-retail inventory trends, shrink reduction', src: 'WMT + TGT 10-K/10-Q' },
]

const features = [
  { title: 'RAG Pipeline', desc: 'Query expansion (35 synonym groups) → ChromaDB retrieval → cross-encoder re-ranking → grounded LLM generation' },
  { title: 'Multi-Backend LLM', desc: 'llama.cpp (local GPU, 7B), Anthropic, or OpenAI — swappable via .env, no vendor lock-in' },
  { title: 'SEC EDGAR Ingestion', desc: 'Auto-fetches MD&A from 10-K/10-Q across 7 companies. One command builds the full index.' },
  { title: 'Cross-Sector Generalization', desc: 'Recall@10 = 1.00 on retail. Pipeline is domain-agnostic, not overfit to restaurant data.' },
  { title: 'Faithfulness Evaluation', desc: 'Strict 74.24%, weighted 75.32% — LLM-as-judge with Claude cross-validation, 11 prompt iterations' },
  { title: 'Cross-Encoder Re-ranking', desc: 'MiniLM-L-6-v2 with hybrid scoring and configurable weight blend between bi-encoder and CE' },
  { title: 'Prompt Injection Defense', desc: 'Input sanitization, delimiters, rate limiting (1/10s), system-level instruction guard' },
  { title: 'LLM Resilience', desc: 'Retry (3x exponential backoff), cross-encoder fallback, backend auto-fallback, GPU memory guard' },
  { title: 'BM25 Caching', desc: 'LRU cache per ticker — 30-50% query latency improvement out of the box' },
  { title: 'Streamlit Dashboard', desc: 'OLED dark mode, 2-view navigation (Q&A + System Analytics), WCAG-contrast colors' },
  { title: 'CI Pipeline', desc: '32 pytest + ruff + mypy. Every push is linted, type-checked, and tested.' },
]

export default function Home() {
  return (
    <>
      <Head>
        <title>RAG Variance Explainer — Multi-Sector Financial RAG Pipeline</title>
        <meta name="description" content="Ask 'why did this financial metric change?' in plain language and get sourced answers from real SEC filings — 7 companies, 4 sectors." />
      </Head>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-[#0A0A0A]/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="h-6 w-6 rounded-md bg-gradient-to-br from-violet-500 to-violet-300" />
            <span className="text-sm font-semibold text-slate-100">RAG Variance Explainer</span>
          </div>
          <nav className="flex items-center gap-6 text-sm text-slate-400">
            <a href="#how-it-works" className="transition-colors hover:text-slate-100">How it works</a>
            <a href="#features" className="transition-colors hover:text-slate-100">Features</a>
            <a href="#use-cases" className="transition-colors hover:text-slate-100">Use cases</a>
            <a href="https://github.com/redsandr/rag-variance-explainer" target="_blank" rel="noopener noreferrer" className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white transition-all hover:bg-violet-500">GitHub</a>
          </nav>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-6 pt-20">
          <div className="pointer-events-none absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-violet-500/10 blur-[120px]" />
          <div className="relative z-10 mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-violet-500/20 bg-violet-500/10 px-4 py-1.5 text-xs font-medium text-violet-300">
              v1.0.0 &middot; 7 Companies &middot; 4 Sectors
            </div>
            <h1 className="mb-4 text-4xl font-bold leading-tight tracking-tight text-slate-100 md:text-6xl">
              Turn a 4-hour variance review into a{' '}
              <span className="gradient-text">3-minute query</span>
            </h1>
            <p className="mx-auto mb-8 max-w-2xl text-lg leading-relaxed text-slate-400">
              A Retrieval-Augmented Generation pipeline that answers{' '}
              <span className="text-slate-200">&quot;why did this financial metric change?&quot;</span>{' '}
              in plain language — sourced directly from real SEC filings. Runs locally, costs nothing per query.
            </p>
            <div className="flex items-center justify-center gap-4">
              <a href="https://github.com/redsandr/rag-variance-explainer" target="_blank" rel="noopener noreferrer" className="rounded-xl bg-violet-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-violet-600/20 transition-all hover:bg-violet-500 hover:shadow-violet-500/30">
                View on GitHub
              </a>
              <a href="https://github.com/redsandr/rag-variance-explainer#quick-start" target="_blank" rel="noopener noreferrer" className="rounded-xl border border-border bg-surface px-6 py-3 text-sm font-medium text-slate-300 transition-all hover:border-slate-600 hover:text-slate-100">
                Quick Start
              </a>
            </div>
          </div>

          {/* Screenshot placeholder */}
          <div className="relative z-10 mt-16 w-full max-w-5xl">
            <div className="glow-lg relative overflow-hidden rounded-2xl border border-border bg-surface">
              <div className="flex aspect-video items-center justify-center bg-gradient-to-br from-surface to-[#0D0D0D]">
                <div className="text-center">
                  <svg className="mx-auto mb-4 h-12 w-12 text-violet-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.41a2.25 2.25 0 013.182 0l2.909 2.91m-18 3.75h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v12a1.5 1.5 0 001.5 1.5zm10.5-11.25h.008v.008h-.008V8.25zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z" />
                  </svg>
                  <p className="text-sm text-slate-500">Dashboard preview</p>
                </div>
              </div>
              <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-[#0A0A0A] to-transparent" />
            </div>
          </div>
        </section>

        {/* Metrics Bar */}
        <section className="border-y border-border bg-surface py-12">
          <div className="mx-auto grid max-w-5xl grid-cols-2 gap-8 px-6 md:grid-cols-4">
            {[
              { label: 'Faithfulness', value: '74.24%', sub: 'Strict', accent: 'text-violet-400' },
              { label: 'Recall@10', value: '1.00', sub: 'Retail', accent: 'text-emerald-400' },
              { label: 'Companies', value: '7', sub: '4 sectors', accent: 'text-violet-400' },
              { label: 'Tests', value: '40', sub: '0 mypy / 0 ruff', accent: 'text-emerald-400' },
            ].map((m) => (
              <div key={m.label} className="text-center">
                <div className={`text-3xl font-bold tracking-tight ${m.accent} md:text-4xl`}>{m.value}</div>
                <div className="mt-1 text-sm font-medium text-slate-100">{m.label}</div>
                <div className="text-xs text-slate-500">{m.sub}</div>
              </div>
            ))}
          </div>
        </section>

        {/* Problem */}
        <section className="mx-auto max-w-4xl px-6 py-24 md:py-32">
          <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-violet-400">The Problem</h2>
          <p className="mb-6 text-2xl font-semibold leading-tight text-slate-100 md:text-3xl">
            Financial analysts spend hours reading MD&A sections every quarter.
          </p>
          <p className="max-w-2xl text-base leading-relaxed text-slate-400">
            Scanning tables, cross-referencing periods, searching for variance drivers — it&apos;s manual, inconsistent, and doesn&apos;t scale.
            Most RAG demos work on one dataset in one domain.{' '}
            <span className="text-slate-200">Generalization is the hard part.</span>{' '}
            This project proves a financial RAG pipeline can generalize across sectors without degrading retrieval quality.
          </p>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="mx-auto max-w-5xl px-6 py-24 md:py-32">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-violet-400">How It Works</h2>
            <p className="text-3xl font-bold text-slate-100 md:text-4xl">Ask. Retrieve. Answer.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-3">
            {[
              { step: '01', title: 'Ask a question', desc: 'Type &quot;Why did labor costs increase?&quot; in plain English. No SQL, no dashboards.', color: 'from-violet-500/20 to-violet-500/5' },
              { step: '02', title: 'Retrieve from filings', desc: 'Query expansion finds synonyms, ChromaDB retrieves chunks, cross-encoder re-ranks by relevance.', color: 'from-violet-500/30 to-violet-500/5' },
              { step: '03', title: 'Get sourced answers', desc: 'LLM generates a grounded answer with citations — color-coded source cards, cross-encoder comparison.', color: 'from-violet-500/40 to-violet-500/5' },
            ].map((s) => (
              <div key={s.step} className={`glow group relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br ${s.color} p-8 transition-all hover:border-violet-500/30`}>
                <div className="mb-4 text-4xl font-black text-violet-500/30">{s.step}</div>
                <h3 className="mb-2 text-lg font-semibold text-slate-100">{s.title}</h3>
                <p className="text-sm leading-relaxed text-slate-400">{s.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Use Cases */}
        <section id="use-cases" className="mx-auto max-w-5xl px-6 py-24 md:py-32">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-violet-400">Use Cases</h2>
            <p className="text-3xl font-bold text-slate-100 md:text-4xl">Real questions, real answers.</p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-border">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <th className="px-6 py-4 font-medium text-slate-300">Question</th>
                  <th className="px-6 py-4 font-medium text-slate-300">Answer includes</th>
                  <th className="px-6 py-4 font-medium text-slate-300">Source</th>
                </tr>
              </thead>
              <tbody>
                {useCases.map((uc) => (
                  <tr key={uc.q} className="border-b border-border last:border-0 hover:bg-white/[0.02]">
                    <td className="px-6 py-4 font-medium text-slate-100">{uc.q}</td>
                    <td className="px-6 py-4 text-slate-400">{uc.a}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center rounded-full border border-violet-500/20 bg-violet-500/10 px-2.5 py-0.5 text-xs font-medium text-violet-300">
                        {uc.src}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="mx-auto max-w-5xl px-6 py-24 md:py-32">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-violet-400">Features</h2>
            <p className="text-3xl font-bold text-slate-100 md:text-4xl">Production-grade RAG, local-first.</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {features.map((f) => (
              <div key={f.title} className="glow group rounded-2xl border border-border bg-surface p-6 transition-all hover:border-violet-500/20">
                <h3 className="mb-2 text-sm font-semibold text-slate-100">{f.title}</h3>
                <p className="text-sm leading-relaxed text-slate-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Architecture */}
        <section className="mx-auto max-w-5xl px-6 py-24 md:py-32">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-violet-400">Architecture</h2>
            <p className="text-3xl font-bold text-slate-100 md:text-4xl">How the pipeline fits together.</p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-border">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <th className="px-6 py-4 font-medium text-slate-300">Component</th>
                  <th className="px-6 py-4 font-medium text-slate-300">Technology</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Embedding', 'nomic-embed-text-v1.5 (768-dim, normalized)'],
                  ['Vector store', 'ChromaDB, cosine distance, metadata-rich'],
                  ['Re-ranking', 'cross-encoder/ms-marco-MiniLM-L-6-v2'],
                  ['Chunking', 'Structure-aware recursive split, 500-token chunks'],
                  ['LLM (default)', 'Qwen2.5-7B-Instruct-Q4_K_M GGUF (RTX 5060, ~2-3s/gen)'],
                  ['Data source', 'SEC EDGAR HTML 10-K/10-Q (MD&A section)'],
                  ['Companies', companies.join(', ')],
                  ['Sectors', sectors.join(', ')],
                  ['Index', '740+ chunks from 40+ filings (~2 years per company)'],
                ].map(([comp, tech]) => (
                  <tr key={comp} className="border-b border-border last:border-0 hover:bg-white/[0.02]">
                    <td className="px-6 py-4 font-medium text-slate-100">{comp}</td>
                    <td className="px-6 py-4 text-slate-400">{tech}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Quick Start */}
        <section className="mx-auto max-w-4xl px-6 py-24 md:py-32">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-violet-400">Quick Start</h2>
            <p className="text-3xl font-bold text-slate-100 md:text-4xl">Get running in 2 minutes.</p>
          </div>
          <div className="overflow-hidden rounded-2xl border border-border">
            <div className="flex border-b border-border">
              <div className="border-b-2 border-violet-500 px-6 py-3 text-sm font-medium text-slate-100">Local model (llama.cpp)</div>
              <div className="px-6 py-3 text-sm text-slate-500">OpenAI API</div>
            </div>
            <div className="bg-[#060606] p-6">
              <pre className="overflow-x-auto text-sm text-slate-300">
                <code>{`# Clone & setup
git clone https://github.com/redsandr/rag-variance-explainer
cd rag-variance-explainer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Build index & run
python src/build_index.py
streamlit run app.py`}</code>
              </pre>
            </div>
          </div>
        </section>

        {/* Roadmap */}
        <section className="mx-auto max-w-4xl px-6 py-24 md:py-32">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-xs font-semibold uppercase tracking-widest text-violet-400">Roadmap</h2>
            <p className="text-3xl font-bold text-slate-100 md:text-4xl">What&apos;s next.</p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            {[
              'International filings (IFRS-based financials)',
              'Multi-turn conversational memory',
              'Docker deployment (single-command setup)',
              'Fine-tuned embedding model on financial corpus',
              'Public hosted demo',
            ].map((item) => (
              <div key={item} className="flex items-center gap-3 rounded-xl border border-border bg-surface px-5 py-4">
                <div className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border-2 border-slate-600">
                  <div className="h-2 w-2 rounded-full bg-slate-600" />
                </div>
                <span className="text-sm text-slate-300">{item}</span>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-8 md:flex-row">
          <div className="flex items-center gap-2 text-sm text-slate-500">
            <span>MIT License</span>
            <span>&middot;</span>
            <span>2026</span>
          </div>
          <div className="flex items-center gap-6 text-sm text-slate-500">
            <a href="https://github.com/redsandr/rag-variance-explainer" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-slate-300">GitHub</a>
            <a href="https://github.com/redsandr/rag-variance-explainer/tree/master/docs" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-slate-300">Docs</a>
          </div>
        </div>
      </footer>
    </>
  )
}
