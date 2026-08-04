// ============================================================
// SEO / Open Graph / Structured data - single source of truth
// Narasi: hasil, bukan teknologi. Target = financial analyst.
// ============================================================

export const SEO = {
  // TODO: ganti dengan domain asli (mis. https://redsandr.github.io/rag-variance-explainer)
  url: 'https://YOUR-DOMAIN.example',

  siteName: 'Variance Explainer',

  title: 'AI Financial Variance Analysis from SEC Filings | Analysis Tool for Financial Analysts',

  description:
    'Analyze SEC 10-K and 10-Q filings with AI. Explain revenue, margin, labor cost, and other financial variances using grounded answers with page-level citations.',

  // TODO: generate og image 1200x630 px, simpan di public/og-image.png
  ogImage: '/og-image.png',

  themeColor: '#f8f7f2',

  twitter: {
    card: 'summary_large_image',
    // TODO: isi handle Twitter/X project (atau hapus)
    handle: '@yourhandle',
  },

  keywords: [
    'financial variance analysis',
    'variance analysis',
    'financial analyst tools',
    'AI financial research',
    'SEC filings',
    '10-K analysis',
    '10-Q analysis',
    'MD&A',
    'earnings analysis',
    'annual report',
    'financial statement analysis',
    'retrieval augmented generation',
    'grounded answers',
    'financial RAG',
  ].join(', '),
};

// FAQ untuk JSON-LD structured data (FAQPage) + sectional FAQ di halaman
export const FAQ = [
  {
    q: 'What is financial variance analysis?',
    a: 'Financial variance analysis is the practice of comparing a reported financial metric - revenue, gross margin, labor cost, operating expense - against a prior period, a budget, or a forecast, then explaining what drove the difference. Instead of just noting that revenue rose, variance analysis identifies the business drivers behind the change, such as price, volume, mix, wage inflation, or foreign exchange.',
  },
  {
    q: 'How do analysts use SEC filings?',
    a: 'Analysts use SEC filings such as the 10-K and 10-Q to find the disclosures, trends, and risks behind a company\u2019s financial results. The Management Discussion and Analysis (MD&A) section is the primary place where management explains why a metric changed, which is why most financial research starts there.',
  },
  {
    q: 'What is MD&A?',
    a: 'Management Discussion and Analysis (MD&A) is the section of a company\u2019s 10-K, 10-Q, or annual report where management explains why financial performance changed between reporting periods. It connects the numbers on the income statement and balance sheet to the underlying business drivers - pricing, volumes, costs, acquisitions, and market conditions.',
  },
  {
    q: 'Can AI analyze 10-K filings?',
    a: 'Yes. This tool indexes the full text of real 10-K filings - including the MD&A section - and retrieves the exact passages that explain a given metric. Answers are generated from those passages and cited to the specific filing and page, so you can verify every claim against the source.',
  },
  {
    q: 'Does this work on 10-Q reports?',
    a: 'Yes. Quarterly 10-Q filings are indexed alongside annual 10-K filings, so you can ask about the latest quarter and compare it with the same period last year. Both filing types are covered by the same retrieval and citation pipeline.',
  },
  {
    q: 'Which companies are supported?',
    a: 'The index currently covers 7 companies across 4 industries: Chipotle (CMG), Darden (DRI), Cracker Barrel (CBRL), Walmart (WMT), Target (TGT), Johnson & Johnson (JNJ), and ExxonMobil (XOM).',
  },
  {
    q: 'Does it run locally?',
    a: 'Yes. The default setup runs fully on your own machine with a local language model and no API keys. Nothing leaves your computer, and there is no per-query cost.',
  },
];

// Long-form SEO content for "What is Financial Variance Analysis?" section
export const VARIANCE_ANALYSIS_CONTENT = {
  title: 'What is Financial Variance Analysis?',
  subtitle: 'The practice behind every earnings call, budget review, and investment thesis.',
  lede: 'Financial variance analysis is the systematic process of comparing a reported financial metric - revenue, gross margin, labor cost, operating expense, or any line item - against a prior period, a budget, or a forecast, and then explaining what drove the difference. It is not enough to know that revenue rose 8%; the analyst must explain whether the increase came from higher prices, higher volumes, a favorable product mix, an acquisition, or a change in accounting policy.',
  sections: [
    {
      heading: 'Why it matters',
      content: 'Every financial decision - from capital allocation to valuation - depends on understanding causation, not just correlation. If gross margin expanded, was it pricing power or a one-time inventory write-down? If labor costs jumped, was it wage inflation, headcount growth, or overtime? Variance analysis separates signal from noise so stakeholders can make decisions grounded in business reality.',
    },
    {
      heading: 'How analysts do it',
      content: 'Traditional variance analysis follows a disciplined workflow: (1) identify the metric that moved, (2) decompose the change into price, volume, mix, and cost components, (3) trace each component to the underlying operational driver, and (4) validate the explanation against the company\u2019s disclosures. The primary source for step 4 is the Management Discussion and Analysis (MD&A) section of SEC 10-K and 10-Q filings, where management is required to explain material changes in financial condition and results of operations.',
    },
    {
      heading: 'Why MD&A is critical',
      content: 'The MD&A is the only section where management connects the numbers to the narrative. It discloses known trends, demands, commitments, and uncertainties that are reasonably likely to affect reported financial information. For an analyst, the MD&A is the ground truth - but finding the relevant paragraph across hundreds of pages of legalistic prose is slow and error-prone.',
    },
    {
      heading: 'Why AI helps',
      content: 'AI-powered retrieval over indexed SEC filings changes the unit economics of variance analysis. Instead of spending hours searching PDFs, the analyst asks a plain-English question - "Why did Chipotle\u2019s labor costs increase?" - and receives a sourced answer in seconds, with every claim cited to the exact filing and page. The RAG (Retrieval-Augmented Generation) pipeline retrieves the relevant MD&A passages, ranks them for relevance, and generates an answer grounded in those passages. This does not replace the analyst\u2019s judgment; it accelerates the evidence-gathering step so the analyst can focus on interpretation and decision-making.',
    },
  ],
};

// Long-form SEO content for "What is MD&A?" section
export const MDA_CONTENT = {
  title: 'What is MD&A?',
  subtitle: 'Management Discussion and Analysis - the narrative behind the numbers.',
  lede: 'Management Discussion and Analysis (MD&A) is the section of a company\u2019s annual report (10-K), quarterly report (10-Q), or other SEC filing where management explains why financial performance changed between reporting periods. It is required by SEC Regulation S-K Item 303 and is the primary source for understanding the business drivers behind reported financial results.',
  sections: [
    {
      heading: 'What MD&A covers',
      content: 'MD&A must address: (1) results of operations - material changes in revenue, expenses, and profitability, broken down by segment or product line where relevant; (2) liquidity and capital resources - cash flow trends, debt obligations, and off-balance-sheet arrangements; (3) critical accounting estimates - judgments that materially affect the financial statements; (4) known trends, demands, commitments, events, and uncertainties that are reasonably likely to have a material effect on financial condition or results of operations.',
    },
    {
      heading: 'Why analysts read MD&A first',
      content: 'The income statement tells you what happened; the MD&A tells you why. A revenue increase could be organic growth, an acquisition, a one-time gain, or a change in revenue recognition. The MD&A discloses which it is. For variance analysis specifically, the MD&A is the authoritative source for the price-volume-mix decomposition and for management\u2019s own explanation of cost drivers such as wage inflation, commodity costs, or foreign exchange.',
    },
    {
      heading: 'The challenge with MD&A',
      content: 'MD&A sections are long (often 20-50 pages), written in legalistic prose, and buried in 200+ page filings. Finding the paragraph that explains a specific metric change requires either reading the entire section or searching with imprecise keywords. Cross-company comparison is even harder - each company structures its MD&A differently, uses different terminology, and emphasizes different drivers.',
    },
  ],
};

// Long-form SEO content for "Why SEC Filings Matter" section
export const SEC_FILINGS_CONTENT = {
  title: 'Why SEC Filings Matter',
  subtitle: '10-K, 10-Q, earnings releases, and annual reports - the primary sources for financial truth.',
  lede: 'Public companies in the U.S. are required to file periodic reports with the Securities and Exchange Commission (SEC). These filings are the authoritative source for a company\u2019s financial results, risks, and management\u2019s own explanation of performance. For financial variance analysis, three filing types are essential:',
  sections: [
    {
      heading: '10-K (Annual Report)',
      content: 'The comprehensive annual filing that includes audited financial statements, the full MD&A, risk factors, business description, and corporate governance. It covers the full fiscal year and is the primary source for year-over-year variance analysis. The 10-K\u2019s MD&A is the most detailed management narrative available.',
    },
    {
      heading: '10-Q (Quarterly Report)',
      content: 'The quarterly filing (three per fiscal year) that includes unaudited financial statements and an abbreviated MD&A focused on material changes from the prior quarter and the same quarter last year. Essential for quarter-over-quarter and year-over-year quarterly variance analysis. The 10-Q captures intra-year dynamics that the annual 10-K may smooth over.',
    },
    {
      heading: 'Earnings Releases (8-K)',
      content: 'Filed via Form 8-K when a company announces quarterly or annual earnings. These press releases provide the headline numbers, management commentary, and often supplemental schedules (segment detail, same-store sales, key metrics) before the full 10-Q or 10-K is filed. They are the fastest signal but lack the depth and legal review of the full filings.',
    },
    {
      heading: 'Annual Report to Shareholders',
      content: 'A separate, often more visually designed document sent to shareholders. It contains the same audited financials as the 10-K but with a different narrative emphasis. Useful for understanding management\u2019s strategic messaging, but the 10-K remains the authoritative legal filing.',
    },
  ],
};