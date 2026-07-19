"use client";

import React from "react";

export default function HeroIllustration() {
  return (
    <svg
      className="hero-illustration-svg w-full h-auto"
      viewBox="0 0 900 420"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Illustration: a messy stack of 300-page SEC filings on the left, transformed by a gold arrow into a clean, cited answer card on the right, with Vernie the mascot below"
    >

  <defs>
    <pattern id="dotGrid" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.8" fill="#1a1a2e" opacity="0.6"/>
    </pattern>
    <filter id="goldGlow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="5" floodColor="#000" floodOpacity="0.5"/>
    </filter>
    <linearGradient id="paperGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stopColor="#1e1e2e"/>
      <stop offset="100%" stopColor="#16161e"/>
    </linearGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stopColor="#F5E6C8"/>
      <stop offset="30%" stopColor="#D4AF37"/>
      <stop offset="70%" stopColor="#B8941F"/>
      <stop offset="100%" stopColor="#8B6914"/>
    </linearGradient>
    <linearGradient id="arrowGrad" x1="0%" y1="50%" x2="100%" y2="50%">
      <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.3"/>
      <stop offset="50%" stopColor="#D4AF37"/>
      <stop offset="100%" stopColor="#F5E6C8"/>
    </linearGradient>
    <radialGradient id="cardGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.15"/>
      <stop offset="100%" stopColor="#D4AF37" stopOpacity="0"/>
    </radialGradient>
  </defs>

  
  <rect width="900" height="420" fill="#0a0a0f"/>
  <rect width="900" height="420" fill="url(#dotGrid)"/>

  
  
  
  <g className="hero-papers" transform="translate(60, 60)" filter="url(#softShadow)">
    
    <rect x="15" y="10" width="140" height="180" rx="3" fill="url(#paperGrad)" stroke="#2a2a3e" strokeWidth="1" transform="rotate(-8, 85, 100)"/>
    <text x="35" y="45" fill="#444" fontSize="8" fontFamily="monospace" transform="rotate(-8, 85, 100)">10-K</text>
    <line x1="30" y1="55" x2="130" y2="55" stroke="#2a2a3e" strokeWidth="1" transform="rotate(-8, 85, 100)"/>
    <line x1="30" y1="65" x2="110" y2="65" stroke="#1e1e2e" strokeWidth="1" transform="rotate(-8, 85, 100)"/>
    <line x1="30" y1="75" x2="120" y2="75" stroke="#1e1e2e" strokeWidth="1" transform="rotate(-8, 85, 100)"/>

    
    <rect x="25" y="25" width="140" height="180" rx="3" fill="url(#paperGrad)" stroke="#2a2a3e" strokeWidth="1" transform="rotate(5, 95, 115)"/>
    <text x="45" y="60" fill="#444" fontSize="8" fontFamily="monospace" transform="rotate(5, 95, 115)">10-Q</text>
    <line x1="40" y1="70" x2="140" y2="70" stroke="#2a2a3e" strokeWidth="1" transform="rotate(5, 95, 115)"/>
    <line x1="40" y1="80" x2="100" y2="80" stroke="#1e1e2e" strokeWidth="1" transform="rotate(5, 95, 115)"/>

    
    <rect x="5" y="40" width="140" height="180" rx="3" fill="url(#paperGrad)" stroke="#2a2a3e" strokeWidth="1" transform="rotate(-12, 75, 130)"/>
    <text x="25" y="75" fill="#444" fontSize="8" fontFamily="monospace" transform="rotate(-12, 75, 130)">MD&amp;A</text>
    <rect x="20" y="85" width="80" height="4" rx="1" fill="#8B4513" opacity="0.6" transform="rotate(-12, 75, 130)"/>
    <rect x="30" y="100" width="60" height="4" rx="1" fill="#B8860B" opacity="0.5" transform="rotate(-12, 75, 130)"/>
    <rect x="15" y="115" width="90" height="4" rx="1" fill="#8B4513" opacity="0.4" transform="rotate(-12, 75, 130)"/>

    
    <rect x="90" y="5" width="100" height="130" rx="3" fill="url(#paperGrad)" stroke="#2a2a3e" strokeWidth="1" transform="rotate(15, 140, 70)"/>
    <text x="105" y="35" fill="#444" fontSize="7" fontFamily="monospace" transform="rotate(15, 140, 70)">NOTE 7</text>
    <line x1="100" y1="42" x2="170" y2="42" stroke="#2a2a3e" strokeWidth="1" transform="rotate(15, 140, 70)"/>

    
    <rect x="35" y="130" width="50" height="30" rx="2" fill="#0f0f1a" stroke="#1e1e2e" transform="rotate(-12, 75, 130)"/>
    <line x1="40" y1="138" x2="80" y2="138" stroke="#2a2a3e" strokeWidth="0.5" transform="rotate(-12, 75, 130)"/>
    <line x1="40" y1="146" x2="75" y2="146" stroke="#2a2a3e" strokeWidth="0.5" transform="rotate(-12, 75, 130)"/>
    <line x1="40" y1="154" x2="70" y2="154" stroke="#2a2a3e" strokeWidth="0.5" transform="rotate(-12, 75, 130)"/>

    
    <rect x="100" y="160" width="50" height="18" rx="9" fill="#1a1a2e" stroke="#333" strokeWidth="1"/>
    <text x="125" y="172" textAnchor="middle" fill="#666" fontSize="9" fontFamily="monospace">p. 147</text>

    
    <text x="75" y="245" textAnchor="middle" fill="#555" fontSize="11" fontFamily="sans-serif" fontWeight="500">300-page filings</text>
  </g>

  
  
  
  <g className="hero-arrow" transform="translate(280, 120)">
    <path d="M 20 80 Q 120 20, 220 80" fill="none" stroke="url(#arrowGrad)" strokeWidth="4" strokeLinecap="round" filter="url(#goldGlow)"/>
    <path d="M 20 80 Q 120 20, 220 80" fill="none" stroke="url(#goldGrad)" strokeWidth="2" strokeLinecap="round"/>
    <polygon points="210,65 240,80 210,95" fill="url(#goldGrad)" filter="url(#goldGlow)"/>
    <circle cx="60" cy="65" r="2" fill="#D4AF37" style={{ animation: 'sparkleFade 1.8s ease-in-out infinite' }}/>
    <circle cx="120" cy="45" r="1.5" fill="#F5E6C8" style={{ animation: 'sparkleFade 2.2s ease-in-out infinite 0.4s' }}/>
    <circle cx="180" cy="60" r="2" fill="#D4AF37" style={{ animation: 'sparkleFade 2s ease-in-out infinite 0.8s' }}/>
  </g>

  
  
  
  <g className="hero-card" transform="translate(520, 50)" filter="url(#softShadow)">
    <rect x="-10" y="-10" width="280" height="260" rx="16" fill="url(#cardGlow)"/>
    <rect x="0" y="0" width="260" height="240" rx="12" fill="#12121e" stroke="#D4AF37" strokeWidth="1.5"/>
    <rect x="2" y="2" width="256" height="236" rx="10" fill="none" stroke="#D4AF37" strokeWidth="0.5" opacity="0.3"/>

    
    <rect x="0" y="0" width="260" height="36" rx="12" fill="#1a1a2e"/>
    <rect x="0" y="18" width="260" height="18" fill="#1a1a2e"/>
    <circle cx="20" cy="18" r="4" fill="#D4AF37" opacity="0.8"/>
    <circle cx="34" cy="18" r="4" fill="#B8941F" opacity="0.6"/>
    <circle cx="48" cy="18" r="4" fill="#8B6914" opacity="0.4"/>
    <text x="130" y="22" textAnchor="middle" fill="#D4AF37" fontSize="11" fontFamily="sans-serif" fontWeight="600" letterSpacing="1">SOURCED ANSWER</text>

    
    <text x="20" y="65" fill="#e8e8f0" fontSize="12" fontFamily="sans-serif">Labor costs rose mainly from</text>
    <text x="20" y="82" fill="#e8e8f0" fontSize="12" fontFamily="sans-serif">wage inflation and minimum wage</text>
    <text x="20" y="99" fill="#e8e8f0" fontSize="12" fontFamily="sans-serif">increases in states like California,</text>
    <text x="20" y="116" fill="#e8e8f0" fontSize="12" fontFamily="sans-serif">partially offset by sales leverage.</text>

    <line x1="20" y1="135" x2="240" y2="135" stroke="#2a2a3e" strokeWidth="1"/>

    
    <rect x="20" y="148" width="130" height="24" rx="6" fill="#1a1a2e" stroke="#D4AF37" strokeWidth="0.5"/>
    <text x="32" y="164" fill="#D4AF37" fontSize="10" fontFamily="monospace">CMG 10-Q, p. 12</text>

    
    <rect x="160" y="148" width="80" height="24" rx="6" fill="#1a1a2e" stroke="#2a8a4e" strokeWidth="0.5"/>
    <text x="172" y="164" fill="#4ade80" fontSize="10" fontFamily="monospace">94%</text>

    
    <rect x="16" y="185" width="4" height="40" rx="2" fill="#D4AF37" opacity="0.6"/>
    <text x="30" y="200" fill="#888" fontSize="9" fontFamily="sans-serif" fontStyle="italic">"...labor costs as a percentage</text>
    <text x="30" y="214" fill="#888" fontSize="9" fontFamily="sans-serif" fontStyle="italic">of revenue increased due to..."</text>

    <text x="130" y="265" textAnchor="middle" fill="#D4AF37" fontSize="11" fontFamily="sans-serif" fontWeight="500">Clean, cited, verified</text>
  </g>

  
  
  
  <g className="hero-vernie" transform="translate(385, 310)">
    <ellipse cx="32" cy="58" rx="14" ry="3" fill="#000" opacity="0.3"/>
    <rect x="20" y="48" width="6" height="10" rx="2" fill="#2a2a3e"/>
    <rect x="38" y="48" width="6" height="10" rx="2" fill="#2a2a3e"/>
    <rect x="18" y="56" width="10" height="5" rx="2" fill="#3a3a5e"/>
    <rect x="36" y="56" width="10" height="5" rx="2" fill="#3a3a5e"/>
    <rect x="14" y="28" width="36" height="24" rx="6" fill="#2a2a3e" stroke="#3a3a5e" strokeWidth="1"/>
    <rect x="20" y="34" width="24" height="3" rx="1.5" fill="#1e1e2e"/>
    <rect x="20" y="40" width="18" height="3" rx="1.5" fill="#1e1e2e"/>
    <rect x="14" y="28" width="36" height="3" rx="1.5" fill="url(#goldGrad)" opacity="0.9"/>
    <rect x="6" y="32" width="10" height="6" rx="3" fill="#2a2a3e"/>
    <rect x="48" y="32" width="10" height="6" rx="3" fill="#2a2a3e"/>
    <rect x="28" y="18" width="8" height="12" rx="2" fill="#3a3a5e" transform="rotate(-15, 32, 24)"/>
    <circle cx="32" cy="12" r="14" fill="none" stroke="url(#goldGrad)" strokeWidth="2.5" filter="url(#goldGlow)"/>
    <circle cx="32" cy="12" r="14" fill="none" stroke="#F5E6C8" strokeWidth="0.5" opacity="0.4"/>
    <circle cx="32" cy="12" r="11" fill="#4a90d9" opacity="0.12"/>
    <circle cx="32" cy="12" r="11" fill="url(#goldGrad)" opacity="0.06"/>
    <ellipse cx="27" cy="7" rx="4" ry="2.5" fill="#fff" opacity="0.25" transform="rotate(-25, 27, 7)"/>
    <circle cx="28" cy="12" r="2.5" fill="#1a1a2e"/>
    <circle cx="36" cy="12" r="2.5" fill="#1a1a2e"/>
    <circle cx="29" cy="11" r="1" fill="#fff"/>
    <circle cx="37" cy="11" r="1" fill="#fff"/>
    <line x1="32" y1="-2" x2="32" y2="-10" stroke="#3a3a5e" strokeWidth="1.5" strokeLinecap="round"/>
    <circle cx="32" cy="-12" r="2.5" fill="url(#goldGrad)"/>
    <circle cx="32" cy="12" r="18" fill="none" stroke="#D4AF37" strokeWidth="0.3" opacity="0.2"/>
  </g>

  <text x="417" y="390" textAnchor="middle" fill="#555" fontSize="10" fontFamily="sans-serif">Vernie</text>
    </svg>
  );
}
