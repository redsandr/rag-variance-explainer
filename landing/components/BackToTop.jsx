"use client";

import { useEffect, useState } from "react";

export default function BackToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    function onScroll() {
      setVisible(window.scrollY > 480);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  function scrollToTop() {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  return (
    <button
      onClick={scrollToTop}
      aria-label="Back to top"
      className="fixed z-40 flex items-center justify-center rounded-full"
      style={{
        bottom: 24,
        right: 24,
        width: 44,
        height: 44,
        background: "var(--accent)",
        color: "var(--btn-text-on-accent)",
        boxShadow: "0 4px 20px rgba(212,175,55,0.35)",
        opacity: visible ? 1 : 0,
        transform: visible ? "translateY(0) scale(1)" : "translateY(12px) scale(0.85)",
        pointerEvents: visible ? "auto" : "none",
        transition: "opacity 0.25s ease, transform 0.25s ease, background 0.15s ease",
      }}
      onMouseEnter={(e) => (e.currentTarget.style.background = "var(--accent-light)")}
      onMouseLeave={(e) => (e.currentTarget.style.background = "var(--accent)")}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 19V5" />
        <path d="M5 12l7-7 7 7" />
      </svg>
    </button>
  );
}
