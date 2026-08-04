import { ROADMAP } from '../data/constants';

export default function RoadmapSection() {
  return (
    <section id="roadmap" className="px-5 sm:px-7 py-24 md:py-28">
      <div className="w-full max-w-[860px] mx-auto">
        <div className="section-head">
          <span className="sec-num">12</span>
          <span className="sec-label">Roadmap</span>
          <span className="sec-line"></span>
        </div>
        <h2 className="text-[clamp(2rem,5.4vw,4.2rem)] font-semibold tracking-[-0.035em] leading-[1.02] m-0 mb-10">What&apos;s next.</h2>
        <ul className="road-list">
          {ROADMAP.map((item, i) => (
            <li key={item}>
              <span className="road-n">{String(i + 1).padStart(2, '0')}</span>
              {item}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}