export const PIPE_QUESTION = "Why did Chipotle's labor costs increase?";

export const HERO_STATS = [
  {
    to: 3,
    label: 'minutes per question, down from ~4 hrs',
    format: (v) => `${Math.round(v)} min`,
    metricLabel: 'per variance question',
    metricSub: 'down from ~4 hours',
  },
  {
    to: 52,
    label: 'right source in top-5, up from 33%',
    format: (v) => `${Math.round(v)}%`,
    metricLabel: 'right source found first try',
    metricSub: 'top-5, up from 33%',
  },
  {
    to: 74,
    label: 'answers verified against the filing',
    format: (v) => `${Math.round(v)}%`,
    metricLabel: 'answers fully verified',
    metricSub: 'restaurant filings',
  },
  {
    to: 7,
    label: 'companies covered, 4 industries',
    format: (v) => `${Math.round(v)}`,
    metricLabel: 'companies covered',
    metricSub: '4 industries',
  },
];

export const METRICS = HERO_STATS.map((s) => ({
  value: s.format(s.to),
  label: s.metricLabel,
  sub: s.metricSub,
}));

export const TRUST_ITEMS = [
  'Grounded in real SEC filings',
  'Every answer cited to a page',
  'Tested across 4 industries',
  'Open source, MIT licensed',
];

export const DEMO_ANALYSES = [
  {
    id: 'cmg-labor',
    question: "Why did Chipotle's labor costs increase?",
    ticker: 'CMG',
    form: '10-Q',
    citation: 'CMG 10-Q, p. 12',
    evidence:
      '"...labor costs as a percentage of revenue increased due to wage inflation and minimum wage increases, partially offset by sales leverage as comparable restaurant sales grew..."',
    answer:
      "Labor costs rose mainly from wage inflation and minimum wage increases in states like California, partially offset by sales leverage as comparable restaurant sales grew.",
    confidence: 94,
  },
  {
    id: 'wmt-ecom',
    question: "What drove Walmart's e-commerce growth?",
    ticker: 'WMT',
    form: '10-K',
    citation: 'WMT 10-K, p. 28',
    evidence:
      '"...e-commerce growth was driven by increased omnichannel penetration and continued adoption of store-fulfilled pickup and delivery..."',
    answer:
      "Growth came mainly from higher omnichannel penetration and continued adoption of store-fulfilled pickup and delivery.",
    confidence: 91,
  },
  {
    id: 'tgt-margin',
    question: "How did Target's gross margin change?",
    ticker: 'TGT',
    form: '10-Q',
    citation: 'TGT 10-Q, p. 19',
    evidence:
      '"...gross margin rate increased, reflecting a favorable shift in merchandise mix and lower promotional and shrink-related costs..."',
    answer:
      "Gross margin improved on a favorable shift in merchandise mix, along with lower promotional activity and reduced shrink.",
    confidence: 88,
  },
  {
    id: 'dri-acq',
    question: "How did the Chuy's acquisition affect Darden's revenue?",
    ticker: 'DRI',
    form: '10-K',
    citation: 'DRI 10-K, p. 41',
    evidence:
      '"...the increase in total revenue was driven in part by the acquisition of Chuy\'s, which contributed segment sales beginning in the fiscal third quarter..."',
    answer:
      "The Chuy's acquisition added incremental segment revenue starting in fiscal Q3, contributing to the total revenue increase for the period.",
    confidence: 90,
  },
  {
    id: 'wmt-tgt-inventory',
    question: 'How do WMT and TGT compare on inventory turnover?',
    ticker: 'WMT + TGT',
    form: '10-K',
    citation: 'WMT 10-K p. 31, TGT 10-K p. 22',
    evidence:
      '"...inventory levels reflect improved in-stock positions and continued efforts to reduce shrink and align inventory with sales trends..."',
    answer:
      'Both retailers cite tighter inventory-to-sales alignment and lower shrink as the main drivers, with Walmart emphasizing in-stock positioning and Target emphasizing markdown discipline.',
    confidence: 86,
  },
];

export const CHART_DATA = [
  { label: 'Top 1', base: 0.18, ce: 0.23 },
  { label: 'Top 3', base: 0.24, ce: 0.45 },
  { label: 'Top 5', base: 0.33, ce: 0.52 },
  { label: 'Top 10', base: 0.55, ce: 0.7 },
];

export const USE_CASES = [
  { q: "Why did Chipotle's labor costs change?", a: 'Wage inflation, CA minimum wage, sales leverage', src: 'CMG 10-K/10-Q' },
  { q: "What drove Walmart's e-commerce growth?", a: 'Omnichannel penetration, store-fulfilled pickup', src: 'WMT 10-K/10-Q' },
  { q: "How did Target's gross margin rate change?", a: 'Merchandise mix, promotions, shrink impact', src: 'TGT 10-K/10-Q' },
  { q: "How did Darden's Chuy's acquisition impact revenue?", a: 'Purchase price, sales contribution, segment profit', src: 'DRI 10-K/10-Q' },
  { q: 'How do WMT and TGT compare on inventory turnover?', a: 'Cross-retail inventory trends, shrink reduction', src: 'WMT + TGT' },
];

export const FEATURES = [
  { t: 'Ask like you would a colleague', d: "No filing jargon required. Ask in plain English and get an answer scoped to what you actually meant." },
  { t: 'Every claim cited to a page', d: 'Each answer points back to the exact filing and page, so you can verify it before it goes in a report.' },
  { t: 'Pulls directly from SEC filings', d: 'Reads straight from 10-Ks and 10-Qs across 7 companies — no manual searching through PDFs.' },
  { t: 'Works across sectors, not just one', d: 'Tested on restaurant, retail, healthcare, and energy filings, with no drop in accuracy between them.' },
  { t: 'Checked against the source', d: "Roughly 3 in 4 answers verified as fully accurate against the original filing text, with ongoing work to push that higher." },
  { t: 'Your filings stay yours', d: 'Runs fully offline on your own machine, or connects to a cloud provider if you prefer — your data, your choice.' },
];

export const ROADMAP = [
  'International filings, not just US-based companies',
  'Follow-up questions in the same conversation, not just one-off queries',
  'One-click setup, no command line required',
  'A version tuned specifically on financial language for even higher accuracy',
  'A public demo anyone can try without installing anything',
];

export const CODE_SNIPPETS = {
  local: `# Clone & setup
git clone https://github.com/redsandr/rag-variance-explainer
cd rag-variance-explainer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Build index & run
python src/build_index.py
streamlit run app.py`,
  openai: `# Clone & setup
git clone https://github.com/redsandr/rag-variance-explainer
cd rag-variance-explainer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Set in .env:
# LLM_BACKEND=openai
# OPENAI_API_KEY=sk-...

python src/build_index.py
streamlit run app.py`,
  claude: `# Clone & setup
git clone https://github.com/redsandr/rag-variance-explainer
cd rag-variance-explainer
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Set in .env:
# LLM_BACKEND=anthropic
# ANTHROPIC_API_KEY=sk-ant-...

python src/build_index.py
streamlit run app.py`,
};

export const PIPE_STEPS = [
  { title: 'Understand the question', label: 'sections searched', kind: 'count', to: 1079, duration: 700, icon: 'search' },
  { title: 'Search the filings', label: 'possible matches', kind: 'count', to: 20, duration: 600, icon: 'filing' },
  { title: 'Rank by relevance', label: 'best match found', kind: 'score', to: 0.91, duration: 700, icon: 'rank' },
  { title: 'Write the answer', label: 'sourced answer', kind: 'writing', icon: 'pen' },
];

export const PIPE_ICONS = {
  search: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.3-4.3" />
    </svg>
  ),
  filing: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
      <path d="M14 2v6h6" />
      <path d="M9 13h6M9 17h6" />
    </svg>
  ),
  rank: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
      <path d="M6 20V10M12 20V4M18 20v-7" />
    </svg>
  ),
  pen: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 20h9" />
      <path d="M16.5 3.5a2.12 2.12 0 013 3L7 19l-4 1 1-4z" />
    </svg>
  ),
};
