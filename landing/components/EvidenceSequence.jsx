import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion, useInView, useReducedMotion } from 'framer-motion';

const stages = [
  { name: 'Question', title: 'Start with a question.', detail: 'Name the metric and reporting period before looking for an explanation.', command: 'ask "Why did the metric change?"', output: 'A question opens an investigation. It is not an answer.' },
  { name: 'Passage', title: 'Find the disclosure.', detail: 'Search the indexed MD&A passages for language relevant to the question.', command: 'retrieve --section "MD&A"', output: 'Relevant passages are leads to examine, not verified causes.' },
  { name: 'Quote check', title: 'Test the wording.', detail: 'Check whether words in a proposed quote occur in retrieved text.', command: 'verify --quoted-text', output: 'Text presence alone does not prove causation or arithmetic.' },
  { name: 'Filing review', title: 'Stop at the source.', detail: 'An analyst still has to inspect the original SEC filing before using an answer.', command: 'review --original-filing', output: 'PENDING REVIEW · No approved example published.' },
];

function ArrowIcon() {
  return <svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10m-4-4 4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}

export default function EvidenceSequence() {
  const sectionRef = useRef(null);
  const inView = useInView(sectionRef, { amount: .25 });
  const reducedMotion = useReducedMotion();
  const [active, setActive] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [finished, setFinished] = useState(false);
  const [visible, setVisible] = useState(true);
  const [typed, setTyped] = useState(stages[0].command);
  const [manual, setManual] = useState(false);

  useEffect(() => {
    const onVisibility = () => setVisible(!document.hidden);
    document.addEventListener('visibilitychange', onVisibility);
    return () => document.removeEventListener('visibilitychange', onVisibility);
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
    }, active === 0 ? 3600 : 3000);
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
    }, 38);
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

  return <section className="sequence wrap" id="tour" ref={sectionRef} aria-labelledby="sequence-title">
    <div className="sequence-header"><div><h2 id="sequence-title">Watch the question meet the source.</h2><p>An illustrated research sequence. These are process steps, not a completed SEC analysis.</p></div><button className="sequence-control" type="button" onClick={finished || !playing ? restart : () => { setPlaying(false); setManual(true); }} aria-label={finished || !playing ? 'Replay research sequence' : 'Pause research sequence'}><svg aria-hidden="true" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d={finished || !playing ? 'M13 7a5 5 0 1 0 .2 2M13 3v4H9' : 'M5 3v10m6-10v10'} stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>{finished || !playing ? 'Replay sequence' : 'Pause sequence'}</button></div>
    <div className="sequence-layout"><div className="sequence-story"><div className="sequence-tabs" aria-label="Research sequence stages">{stages.map((stage, index) => <button type="button" key={stage.name} className={`sequence-tab ${index === active ? 'is-current' : ''}`} aria-pressed={index === active} aria-controls="sequence-description" onClick={() => select(index)}><span className="sequence-index">0{index + 1}</span><span className="sequence-tab-name">{stage.name}</span><ArrowIcon /><span className={`sequence-timer ${index === active && playing && inView && !reducedMotion ? 'is-running' : ''}`} key={`${index}-${active}-${playing}`} aria-hidden="true" /></button>)}</div><div id="sequence-description" className="sequence-description" aria-live={manual ? 'polite' : 'off'} aria-atomic="true"><AnimatePresence initial={false} mode="wait"><motion.div key={active} initial={reducedMotion ? false : { opacity: 0, y: 9 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -7 }} transition={{ duration: reducedMotion ? 0 : .2 }}><h3>{stages[active].title}</h3><p>{stages[active].detail}</p></motion.div></AnimatePresence></div></div>
      <div className="sequence-terminal" aria-label="Illustrative research terminal"><div className="terminal-bar"><span className="terminal-lights" aria-hidden="true"><i></i><i></i><i></i></span><span>variance-explainer / process preview</span><span className="terminal-illustrative">Illustrative</span></div><div className="terminal-screen"><div className="terminal-context">RESEARCH WORKFLOW <span>·</span> NOT A LIVE QUERY</div><div className="terminal-command"><span aria-hidden="true">$</span> {typed}<span className="terminal-caret" aria-hidden="true" /></div><div className="terminal-rule" /><AnimatePresence initial={false} mode="wait"><motion.div className="terminal-output" key={active} initial={reducedMotion ? false : { opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -8 }} transition={{ duration: reducedMotion ? 0 : .25 }}><span className="terminal-output-label">{stages[active].name} / research boundary</span><p>{stages[active].output}</p></motion.div></AnimatePresence><div className="terminal-bottom"><span>{String(active + 1).padStart(2, '0')} / 04</span><span className="terminal-bottom-status">Original filing review required</span></div></div></div></div>
  </section>;
}
