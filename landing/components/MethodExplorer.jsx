import { useState } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'framer-motion';

const steps = [
  {
    id: 'retrieve',
    label: 'Retrieve',
    heading: 'Find the relevant passage.',
    detail: 'The system searches indexed MD&A text from selected SEC 10-K and 10-Q filings, then ranks passages relevant to the question.',
    boundary: 'A relevant passage is a lead for research, not evidence that a proposed explanation is true.',
  },
  {
    id: 'quote',
    label: 'Check the quote',
    heading: 'Match words to retrieved text.',
    detail: 'A structured answer references source passages. The verifier checks whether its quoted words occur in those retrieved passages.',
    boundary: 'A quote match confirms text presence. It does not prove a causal claim or a calculation.',
  },
  {
    id: 'filing',
    label: 'Review the filing',
    heading: 'Read the original disclosure.',
    detail: 'An analyst checks the filing itself, including the metric, reporting period, wording, and whether management explicitly connects a cause to the change.',
    boundary: 'If the filing does not establish a cause, the explanation must remain unconfirmed.',
  },
];

export default function MethodExplorer() {
  const [activeId, setActiveId] = useState(steps[0].id);
  const reducedMotion = useReducedMotion();
  const activeStep = steps.find((step) => step.id === activeId);

  return (
    <div className="method-explorer">
      <div className="method-steps" aria-label="Explore the research method">
        {steps.map((step, index) => (
          <button
            className={`method-step ${step.id === activeId ? 'is-active' : ''}`}
            key={step.id}
            type="button"
            aria-pressed={step.id === activeId}
            aria-controls="method-detail"
            onClick={() => setActiveId(step.id)}
          >
            {step.id === activeId && <motion.span className="method-active-line" layoutId="method-active-line" transition={reducedMotion ? { duration: 0 } : { type: 'spring', stiffness: 360, damping: 34 }} />}
            <span className="method-step-number">0{index + 1}</span>
            <span className="method-step-label">{step.label}</span>
            <svg className="method-step-arrow" aria-hidden="true" viewBox="0 0 20 20" fill="none"><path d="M4 10h11m-5-5 5 5-5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </button>
        ))}
      </div>
      <div id="method-detail" className="method-detail" aria-live="polite" aria-atomic="true">
        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={activeStep.id}
            initial={reducedMotion ? { opacity: 1 } : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={reducedMotion ? { opacity: 1 } : { opacity: 0, y: -8 }}
            transition={{ duration: reducedMotion ? 0 : 0.24, ease: [0.16, 1, 0.3, 1] }}
          >
            <span className="field-label">Research step / 0{steps.indexOf(activeStep) + 1}</span>
            <h3>{activeStep.heading}</h3>
            <p>{activeStep.detail}</p>
            <div className="method-boundary"><span>Evidence boundary</span><p>{activeStep.boundary}</p></div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
