import { useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';
import { ArrowIcon } from './SiteLayout';

const steps = [
  {
    id: 'question', label: 'Ask', title: 'Start with the reported change.',
    detail: 'An analyst begins with a metric and a period. The question determines which filing passages the system looks for.',
    annotation: 'A question frames the search. It is not a financial finding.',
    activeField: 'question',
  },
  {
    id: 'retrieve', label: 'Find evidence', title: 'Find the relevant disclosure.',
    detail: 'The prototype searches indexed MD&A passages in selected SEC 10-K and 10-Q filings and ranks possible leads.',
    annotation: 'A retrieved passage may be relevant without establishing a cause.',
    activeField: 'source',
  },
  {
    id: 'check', label: 'Check the quote', title: 'Check the words, not just the citation.',
    detail: 'When a structured answer contains a quotation, the verifier checks that its words occur in the cited retrieved passage.',
    annotation: 'A text match cannot prove the arithmetic or the explanation.',
    activeField: 'quote',
  },
  {
    id: 'review', label: 'Review', title: 'Return to the original filing.',
    detail: 'An analyst checks the metric, period, wording and whether management explicitly connects the proposed cause to the change.',
    annotation: 'No example is published as a verified financial finding until this review is complete.',
    activeField: 'review',
  },
];

const workpaper = [
  { id: 'question', name: 'Research question', value: 'Why did this metric change?', note: 'Illustrative prompt' },
  { id: 'source', name: 'Filing passage', value: 'Passage withheld', note: 'No approved SEC excerpt on this site' },
  { id: 'quote', name: 'Quoted evidence', value: 'Quote not available', note: 'No quote match claimed' },
  { id: 'review', name: 'Analyst conclusion', value: 'Not yet approved', note: 'Original filing review pending' },
];

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
          {activeIndex < steps.length - 1 ? <button type="button" onClick={() => setActiveIndex(activeIndex + 1)}>Next stage <ArrowIcon /></button> : <a href="/method">Read the method <ArrowIcon /></a>}
        </div>
      </div>
      <div className="walkthrough-paper" aria-label="Illustrative research workpaper, no verified SEC answer">
        <div className="walkthrough-paper-head"><span>Research workpaper</span><span>Illustrative layout · not a live query</span></div>
        <div className="walkthrough-paper-fields">
          {workpaper.map((field) => <div key={field.id} className={`walkthrough-field ${step.activeField === field.id ? 'is-in-focus' : ''}`}>
            <span>{field.name}</span><strong>{field.value}</strong><small>{field.note}</small>
          </div>)}
        </div>
        <div className="walkthrough-paper-foot">No fabricated quote, page number, or causal finding is presented.</div>
      </div>
    </div>
  </div>;
}
