import { useState, useRef, useEffect } from 'react';
import { FAQ } from '../data/seo';

function FAQItem({ item, index }) {
  const [open, setOpen] = useState(false);
  const contentRef = useRef(null);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    if (contentRef.current) {
      setHeight(open ? contentRef.current.scrollHeight : 0);
    }
  }, [open]);

  return (
    <details className="faq-item" open={open} onToggle={() => setOpen(!open)}>
      <summary>
        {item.q}
        <span className="faq-x">{open ? '×' : '+'}</span>
      </summary>
      <div className="faq-a-wrapper" style={{ overflow: 'hidden', transition: 'height 0.4s cubic-bezier(0.16, 1, 0.3, 1)', height: open ? height : 0 }}>
        <div className="faq-a" ref={contentRef}>{item.a}</div>
      </div>
    </details>
  );
}

export default function FAQSection() {
  return (
    <section id="faq" className="px-5 sm:px-7 py-24 md:py-28">
      <div className="w-full max-w-[860px] mx-auto">
        <div className="section-head">
          <span className="sec-num">05</span>
          <span className="sec-label">FAQ</span>
          <span className="sec-line"></span>
        </div>
        <h2 className="text-[clamp(2rem,5.4vw,4.2rem)] font-semibold tracking-[-0.035em] leading-[1.02] m-0 mb-10">Frequently Asked Questions</h2>

        <dl className="faq-list">
          {FAQ.map((item, idx) => (
            <FAQItem key={idx} item={item} index={idx} />
          ))}
        </dl>
      </div>
    </section>
  );
}