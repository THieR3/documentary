import React from "react";
import { AbsoluteFill, random, useCurrentFrame } from "remotion";

export const Vignette: React.FC<{ amount: number }> = ({ amount }) =>
  amount > 0 ? (
    <AbsoluteFill style={{ pointerEvents: "none", background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,${0.75 * amount}) 100%)` }} />
  ) : null;

// Film grain: SVG turbulence whose seed changes every 2 frames.
export const Grain: React.FC<{ amount: number }> = ({ amount }) => {
  const frame = useCurrentFrame();
  if (amount <= 0) return null;
  const seed = Math.floor(random(`grain-${Math.floor(frame / 2)}`) * 1000);
  return (
    <AbsoluteFill style={{ pointerEvents: "none", opacity: 0.12 * amount, mixBlendMode: "overlay" }}>
      <svg width="100%" height="100%">
        <filter id={`g${seed}`}>
          <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves={2} seed={seed} stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter={`url(#g${seed})`} />
      </svg>
    </AbsoluteFill>
  );
};
