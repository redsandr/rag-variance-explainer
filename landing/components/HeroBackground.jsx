export default function HeroBackground() {
  return (
    <div
      aria-hidden="true"
      style={{
        position: 'absolute',
        inset: 0,
        zIndex: 0,
        pointerEvents: 'none',
        overflow: 'hidden',
      }}
    >
      {/* Dot grid pattern */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'radial-gradient(circle, var(--border) 1px, transparent 1px)',
          backgroundSize: '32px 32px',
          opacity: 0.5,
        }}
      />

      {/* Large gold glow — top left */}
      <div
        style={{
          position: 'absolute',
          top: '-20%',
          left: '-10%',
          width: '60%',
          height: '80%',
          background: 'radial-gradient(ellipse at center, rgba(212,175,55,0.08) 0%, transparent 70%)',
        }}
      />

      {/* Large gold glow — bottom right */}
      <div
        style={{
          position: 'absolute',
          bottom: '-10%',
          right: '-5%',
          width: '50%',
          height: '60%',
          background: 'radial-gradient(ellipse at center, rgba(212,175,55,0.05) 0%, transparent 70%)',
        }}
      />

      {/* Subtle decorative ring — top right */}
      <div
        style={{
          position: 'absolute',
          top: '-5%',
          right: '5%',
          width: '30vmin',
          height: '30vmin',
          borderRadius: '50%',
          border: '1px solid rgba(212,175,55,0.06)',
        }}
      />

      {/* Subtle decorative ring — bottom left */}
      <div
        style={{
          position: 'absolute',
          bottom: '5%',
          left: '2%',
          width: '20vmin',
          height: '20vmin',
          borderRadius: '50%',
          border: '1px solid rgba(212,175,55,0.04)',
        }}
      />
    </div>
  );
}
