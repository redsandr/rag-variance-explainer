import { useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { ArrowIcon } from './SiteLayout';

const steps = [
  {
    id: 'question', label: 'Question', title: 'Start with one reported change.',
    detail: 'What drove the change in Johnson & Johnson’s Europe sales in fiscal Q1 2026?',
    annotation: 'This is a reviewed example from a local run, not a question submitted to a live model on this website.',
    activeField: 'question',
  },
  {
    id: 'retrieve', label: 'Finding', title: 'Separate reported growth from its components.',
    detail: 'J&J reported that sales by its companies in Europe grew 14.5% versus fiscal Q1 2025. It attributed 11.8 percentage points of that growth to positive currency impact and 2.7 percentage points to operational growth. Currency was the larger reported component.',
    annotation: 'The local run matched a quotation; these narrow claims were separately checked against the original filing body.',
    activeField: 'source',
  },
  {
    id: 'check', label: 'Quotation', title: 'Read management’s exact wording.',
    detail: '“In the fiscal first quarter of 2026, sales by companies in Europe achieved growth of 14.5%, which included operational growth of 2.7% and a positive currency impact of 11.8%.”',
    annotation: 'In this filing, operational excludes the effect of translational currency. A quote match alone cannot verify every claim.',
    activeField: 'quote',
  },
  {
    id: 'review', label: 'Filing & limits', title: 'Open the original disclosure.',
    detail: 'The original 10-Q’s Item 2 compares fiscal Q1 2026 with fiscal Q1 2025. This regional breakdown does not identify every business driver or independently calculate a sales bridge.',
    annotation: 'Not investment advice. Human review of this case is not a general accuracy guarantee for the model.',
    activeField: 'review',
  },
];

const workpaper = [
  { id: 'question', name: 'Research question', value: 'Why did J&J Europe sales change?', note: 'Fiscal Q1 2026 versus fiscal Q1 2025' },
  { id: 'source', name: 'Reviewed finding', value: '14.5% reported growth', note: '11.8 pp currency · 2.7 pp operational' },
  { id: 'quote', name: 'Quoted evidence', value: 'Original 10-Q wording', note: 'Read the full excerpt at this stage' },
  { id: 'review', name: 'Original filing', value: 'J&J Form 10-Q', note: 'Item 2 · Analysis of consolidated sales' },
];

const filingUrl = 'https://www.sec.gov/Archives/edgar/data/200406/000020040626000087/jnj-20260329.htm';

export default function ExampleWalkthrough({ compact = false }) {
  const [activeIndex, setActiveIndex] = useState(0);
  const reducedMotion = useReducedMotion();
  const step = steps[activeIndex];

  return <div className={`walkthrough ${compact ? 'walkthrough--compact' : ''}`}>
    <div className="walkthrough-controls" aria-label="Explore the research stages">
      {steps.map((item, index) => <button type="button" key={item.id} className={`walkthrough-step ${index === activeIndex ? 'is-active' : ''}`} aria-pressed={index === activeIndex} aria-controls="walkthrough-detail" onClick={() => setActiveIndex(index)}>
        <span className="walkthrough-step-index">0{index + 1}</span><span>{item.label}</span>
        {index === activeIndex && <motion.span className="walkthrough-active-edge" layoutId={compact ? 'home-walkthrough-edge' : 'example-walkthrough-edge'} transition={reducedMotion ? { duration: 0 } : { type: 'spring', stiffness: 360, damping: 38 }} />}
      </button>)}
    </div>
    <div className="walkthrough-body">
      <div className="walkthrough-copy" id="walkthrough-detail" aria-live="polite" aria-atomic="true">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div key={step.id} initial={reducedMotion ? false : { opacity: .4, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }} transition={{ duration: reducedMotion ? 0 : .28, ease: [0.16, 1, 0.3, 1] }}>
            <h3>{step.title}</h3><p>{step.detail}</p><p className="walkthrough-annotation">{step.annotation}</p>
          </motion.div>
        </AnimatePresence>
        <div className="walkthrough-next">
          {activeIndex > 0 && <button type="button" onClick={() => setActiveIndex(activeIndex - 1)}>Previous stage</button>}
          {activeIndex < steps.length - 1 ? <button type="button" onClick={() => setActiveIndex(activeIndex + 1)}>Next stage <ArrowIcon /></button> : <a href={filingUrl} target="_blank" rel="noopener noreferrer">Open SEC filing <ArrowIcon diagonal /></a>}
        </div>
      </div>
      <div className="walkthrough-paper" aria-label="Reviewed JNJ Europe sales case, static walkthrough">
        <div className="walkthrough-paper-head"><span>JNJ / Europe sales</span><span>Reviewed case · static walkthrough</span></div>
        <div className="walkthrough-paper-fields">
          {workpaper.map((field) => <div key={field.id} className={`walkthrough-field ${step.activeField === field.id ? 'is-in-focus' : ''}`}>
            <span>{field.name}</span><strong>{field.value}</strong><small>{field.note}</small>
          </div>)}
        </div>
        <div className="walkthrough-paper-foot">Source: J&J 10-Q · March 29, 2026 · <a href={filingUrl} target="_blank" rel="noopener noreferrer">Read original filing ↗</a></div>
      </div>
    </div>
  </div>;
}
