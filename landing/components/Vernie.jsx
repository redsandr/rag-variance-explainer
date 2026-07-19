"use client";

import React from "react";

const Vernie = ({ pose = "idle", size = 64, className = "" }) => {
  const poses = {
    idle: {
      bodyY: 0,
      antennaOpacity: [1, 0.4, 1],
      antennaDuration: "3s",
      lensGlow: false,
      sparkles: false,
      dots: false,
      wave: false,
      questions: false,
      darkLens: false,
    },
    searching: {
      bodyY: 0,
      antennaOpacity: [1, 0.2, 1],
      antennaDuration: "0.5s",
      lensGlow: true,
      sparkles: false,
      dots: false,
      wave: false,
      questions: false,
      darkLens: false,
    },
    found: {
      bodyY: 0,
      antennaOpacity: [1, 0.6, 1],
      antennaDuration: "1s",
      lensGlow: true,
      sparkles: true,
      dots: false,
      wave: false,
      questions: false,
      darkLens: false,
    },
    thinking: {
      bodyY: 0,
      antennaOpacity: [1, 0.4, 1],
      antennaDuration: "3s",
      lensGlow: false,
      sparkles: false,
      dots: true,
      wave: false,
      questions: false,
      darkLens: false,
    },
    waving: {
      bodyY: 0,
      antennaOpacity: [1, 0.4, 1],
      antennaDuration: "3s",
      lensGlow: false,
      sparkles: false,
      dots: false,
      wave: true,
      questions: false,
      darkLens: false,
    },
    confused: {
      bodyY: 0,
      antennaOpacity: [1, 0.4, 1],
      antennaDuration: "3s",
      lensGlow: false,
      sparkles: false,
      dots: false,
      wave: false,
      questions: true,
      darkLens: true,
    },
  };

  const currentPose = poses[pose] || poses.idle;
  const scale = size / 64;

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      className={className}
      style={{
        animation: pose === "idle" || pose === "found" 
          ? "vernieBounce 2s ease-in-out infinite" 
          : "none",
      }}
    >
      <defs>
        <filter id={`glow-${pose}`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <linearGradient id={`gold-${pose}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F5E6C8" />
          <stop offset="50%" stopColor="#D4AF37" />
          <stop offset="100%" stopColor="#B8941F" />
        </linearGradient>
      </defs>

      {/* Shadow */}
      <ellipse cx="32" cy="58" rx="14" ry="3" fill="#000" opacity="0.3" />

      {/* Legs */}
      <rect x="20" y="48" width="6" height="10" rx="2" fill="#2a2a3e" />
      <rect x="38" y="48" width="6" height="10" rx="2" fill="#2a2a3e" />

      {/* Feet */}
      <rect x="18" y="56" width="10" height="5" rx="2" fill="#3a3a5e" />
      <rect x="36" y="56" width="10" height="5" rx="2" fill="#3a3a5e" />

      {/* Body */}
      <rect x="14" y="28" width="36" height="24" rx="6" fill="#2a2a3e" stroke="#3a3a5e" strokeWidth="1" />
      <rect x="20" y="34" width="24" height="3" rx="1.5" fill="#1e1e2e" />
      <rect x="20" y="40" width="18" height="3" rx="1.5" fill="#1e1e2e" />
      <rect x="14" y="28" width="36" height="3" rx="1.5" fill={`url(#gold-${pose})`} opacity="0.9" />

      {/* Arms */}
      <rect
        x="6"
        y="32"
        width="10"
        height="6"
        rx="3"
        fill="#2a2a3e"
        style={{
          transform: currentPose.wave ? "rotate(-20deg)" : "none",
          transformOrigin: "16px 35px",
          animation: currentPose.wave ? "vernieWave 1s ease-in-out infinite" : "none",
        }}
      />
      <rect x="48" y="32" width="10" height="6" rx="3" fill="#2a2a3e" />

      {/* Handle */}
      <rect x="28" y="18" width="8" height="12" rx="2" fill="#3a3a5e" transform="rotate(-15, 32, 24)" />

      {/* Magnifying glass rim */}
      <circle
        cx="32"
        cy="12"
        r="14"
        fill="none"
        stroke={`url(#gold-${pose})`}
        strokeWidth="2.5"
        filter={currentPose.lensGlow ? `url(#glow-${pose})` : "none"}
        opacity={currentPose.darkLens ? 0.5 : 1}
      />
      <circle cx="32" cy="12" r="14" fill="none" stroke="#F5E6C8" strokeWidth="0.5" opacity="0.4" />

      {/* Lens */}
      <circle cx="32" cy="12" r="11" fill="#4a90d9" opacity={currentPose.darkLens ? 0.05 : 0.12} />
      <circle cx="32" cy="12" r="11" fill={`url(#gold-${pose})`} opacity={currentPose.lensGlow ? 0.15 : 0.06} />

      {/* Lens highlight */}
      <ellipse cx="27" cy="7" rx="4" ry="2.5" fill="#fff" opacity="0.25" transform="rotate(-25, 27, 7)" />

      {/* Eyes */}
      <circle cx="28" cy="12" r="2.5" fill="#1a1a2e" />
      <circle cx="36" cy="12" r="2.5" fill="#1a1a2e" />
      <circle cx="29" cy="11" r="1" fill="#fff" />
      <circle cx="37" cy="11" r="1" fill="#fff" />

      {/* Antenna */}
      <line x1="32" y1="-2" x2="32" y2="-10" stroke="#3a3a5e" strokeWidth="1.5" strokeLinecap="round" />
      <circle cx="32" cy="-12" r="2.5" fill={`url(#gold-${pose})`}>
        <animate
          attributeName="opacity"
          values={currentPose.antennaOpacity.join(";")}
          dur={currentPose.antennaDuration}
          repeatCount="indefinite"
        />
      </circle>

      {/* Outer glow ring */}
      <circle cx="32" cy="12" r="18" fill="none" stroke="#D4AF37" strokeWidth="0.3" opacity="0.2" />

      {/* Sparkles (found pose) */}
      {currentPose.sparkles && (
        <>
          <circle cx="18" cy="6" r="1.5" fill="#D4AF37" opacity="0.8">
            <animate attributeName="opacity" values="0.8;0.2;0.8" dur="1.5s" repeatCount="indefinite" />
          </circle>
          <circle cx="46" cy="4" r="1" fill="#F5E6C8" opacity="0.6">
            <animate attributeName="opacity" values="0.6;0.1;0.6" dur="2s" repeatCount="indefinite" />
          </circle>
          <circle cx="14" cy="18" r="1.2" fill="#D4AF37" opacity="0.7">
            <animate attributeName="opacity" values="0.7;0.2;0.7" dur="1.8s" repeatCount="indefinite" />
          </circle>
        </>
      )}

      {/* Thinking dots */}
      {currentPose.dots && (
        <g transform="translate(24, -20)">
          <circle cx="0" cy="0" r="2" fill="#888" opacity="0.8">
            <animate attributeName="opacity" values="0.8;0.2;0.8" dur="1s" repeatCount="indefinite" />
          </circle>
          <circle cx="8" cy="0" r="2" fill="#888" opacity="0.6">
            <animate attributeName="opacity" values="0.6;0.2;0.6" dur="1s" begin="0.3s" repeatCount="indefinite" />
          </circle>
          <circle cx="16" cy="0" r="2" fill="#888" opacity="0.4">
            <animate attributeName="opacity" values="0.4;0.1;0.4" dur="1s" begin="0.6s" repeatCount="indefinite" />
          </circle>
        </g>
      )}

      {/* Question marks (confused pose) */}
      {currentPose.questions && (
        <>
          <text x="10" y="-8" fill="#888" fontSize="10" fontFamily="sans-serif" fontWeight="bold">?</text>
          <text x="46" y="-6" fill="#888" fontSize="8" fontFamily="sans-serif" fontWeight="bold">?</text>
        </>
      )}
    </svg>
  );
};

export default Vernie;
