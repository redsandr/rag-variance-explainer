import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useInView, useReducedMotion } from 'framer-motion';

const stages = [
  { name: 'The question', title: 'Every explanation starts with a question.', detail: 'Name the metric and period before searching for a reason.', command: 'ask "Why did the metric change?"', output: 'A question opens an investigation. It is not an answer.', scene: 'question' },
  { name: 'The passage', title: 'Go where the filing speaks.', detail: 'Look for relevant language in indexed MD&A passages.', command: 'retrieve --section "MD&A"', output: 'Relevant passages are leads, not verified causes.', scene: 'passage' },
  { name: 'The check', title: 'Words must survive a closer look.', detail: 'Compare proposed quotations with the retrieved passage.', command: 'verify --quoted-text', output: 'A text match does not establish arithmetic or causation.', scene: 'check' },
  { name: 'The review', title: 'The final word belongs to the filing.', detail: 'An analyst must inspect the original SEC filing before using any explanation.', command: 'review --original-filing', output: 'PENDING REVIEW · No approved example published.', scene: 'review' },
];

function ResearchScene({ scene }) {
  return <div className={`research-art research-art--${scene}`} aria-hidden="true">
    <div className="research-orbit research-orbit--outer" />
    <div className="research-orbit research-orbit--inner" />
    <div className="research-art-core">
      {scene === 'question' && <div className="research-question-mark">?</div>}
      {scene === 'passage' && <div className="research-document"><span>SEC / MD&amp;A</span><i /><i /><i className="research-highlight" /><i /><i /></div>}
      {scene === 'check' && <div className="research-quotation"><span>“</span><i /><i /><i className="research-highlight" /><b>TEXT MATCH ≠ VERIFIED CLAIM</b></div>}
      {scene === 'review' && <div className="research-review-mark"><span>!</span><small>HUMAN REVIEW</small></div>}
    </div>
    <span className="research-coordinate research-coordinate--top">SOURCE / SEC EDGAR</span>
    <span className="research-coordinate research-coordinate--bottom">ILLUSTRATIVE PROCESS · NOT A LIVE QUERY</span>
  </div>;
}

export default function EvidenceSequence() {
  const sectionRef = useRef(null);
  const inView = useInView(sectionRef, { amount: .2 });
  const reducedMotion = useReducedMotion();
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [finished, setFinished] = useState(false);
  const [visible, setVisible] = useState(true);
  const [manual, setManual] = useState(false);
  const [typed, setTyped] = useState(stages[0].command);

  useEffect(() => {
    const update = () => setVisible(!document.hidden);
    document.addEventListener('visibilitychange', update);
    return () => document.removeEventListener('visibilitychange', update);
  }, []);

  useEffect(() => { if (reducedMotion) setPlaying(false); }, [reducedMotion]);

  useEffect(() => {
    if (reducedMotion || !inView || !visible || !playing || finished) return;
    const timer = window.setTimeout(() => {
      if (active === stages.length - 1) {
        setPlaying(false);
        setFinished(true);
      } else {
        setActive(active + 1);
      }
    }, active === 0 ? 4200 : 3800);
    return () => window.clearTimeout(timer);
  }, [active, finished, inView, playing, reducedMotion, visible]);

  useEffect(() => {
    const command = stages[active].command;
    if (reducedMotion || !inView || !visible || !playing) {
      setTyped(command);
      return;
    }
    setTyped('');
    let index = 0;
    const timer = window.setInterval(() => {
      index += 1;
      setTyped(command.slice(0, index));
      if (index >= command.length) window.clearInterval(timer);
    }, 45);
    return () => window.clearInterval(timer);
  }, [active, inView, playing, reducedMotion, visible]);

  const select = (index) => {
    setActive(index);
    setPlaying(false);
    setManual(true);
    setFinished(index === stages.length - 1);
  };

  const restart = () => {
    setActive(0);
    setFinished(false);
    setPlaying(!reducedMotion);
    setManual(false);
  };

  const stage = stages[active];

  return <section className="sequence" id="tour" ref={sectionRef} aria-labelledby="sequence-title">
    <div className="sequence-intro wrap"><span>01 / THE INVESTIGATION</span><h2 id="sequence-title">A question is not an answer.</h2><p>Follow the research to the point where human review begins.</p></div>
    <div className={`sequence-stage sequence-stage--${stage.scene}`}>
      <div className="sequence-stage-inner wrap">
        <div className="sequence-scene" aria-hidden="true"><AnimatePresence mode="wait" initial={false}><motion.div key={stage.scene} className="sequence-scene-frame" initial={reducedMotion ? false : { opacity: 0, scale: .88, rotate: -5 }} animate={{ opacity: 1, scale: 1, rotate: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, scale: 1.1, rotate: 5 }} transition={{ duration: reducedMotion ? 0 : .65, ease: [0.16, 1, 0.3, 1] }}><ResearchScene scene={stage.scene} /></motion.div></AnimatePresence></div>
        <div className="sequence-narrative" id="sequence-description" aria-live={manual ? 'polite' : 'off'} aria-atomic="true"><span className="sequence-narrative-index">0{active + 1} <span>/ 04</span></span><AnimatePresence mode="wait" initial={false}><motion.div key={stage.name} initial={reducedMotion ? false : { opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -18 }} transition={{ duration: reducedMotion ? 0 : .38 }}><span className="sequence-narrative-label">{stage.name}</span><h3>{stage.title}</h3><p>{stage.detail}</p></motion.div></AnimatePresence></div>
        <div className="sequence-console" aria-label="Illustrative research terminal"><div><span className="console-led" /> RESEARCH / NOT LIVE</div><div className="console-command"><span aria-hidden="true">›</span> {typed}<span className="console-caret" aria-hidden="true" /></div><div className="console-output" aria-live={manual ? 'polite' : 'off'}>{stage.output}</div></div>
      </div>
    </div>
    <div className="sequence-controls wrap"><div className="sequence-tabs" aria-label="Research sequence stages">{stages.map((item, index) => <button type="button" className={`sequence-tab ${index === active ? 'is-current' : ''}`} key={item.name} aria-pressed={index === active} aria-controls="sequence-description" onClick={() => select(index)}><span>0{index + 1}</span>{item.name}<i className={`sequence-timer ${index === active && playing && inView && visible && !reducedMotion ? 'is-running' : ''}`} key={`${active}-${playing}-${visible}`} aria-hidden="true" /></button>)}</div><button type="button" className="sequence-control" onClick={finished || !playing ? restart : () => { setPlaying(false); setManual(true); }} aria-label={finished || !playing ? 'Replay research sequence' : 'Pause research sequence'}>{finished || !playing ? '↺ Replay' : 'Ⅱ Pause'}</button></div>
  </section>;
}
