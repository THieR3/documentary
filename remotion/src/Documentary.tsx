import React, { createContext, useContext } from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, useCurrentFrame } from "remotion";
import type { DocProps, Segment, Style } from "./types";
import { VisualLayer } from "./components/Visual";
import { OverlayLayer } from "./components/Overlays";
import { Captions } from "./components/Captions";
import { Grain, Vignette } from "./components/Texture";

export const StyleCtx = createContext<Style | null>(null);
export const useStyle = () => {
  const s = useContext(StyleCtx);
  if (!s) throw new Error("StyleCtx missing");
  return s;
};

const SegmentView: React.FC<{ seg: Segment }> = ({ seg }) => {
  const frame = useCurrentFrame(); // relative to Sequence start (= startFrame - transitionFrames)
  const t = seg.transitionFrames;
  let opacity = 1;
  let translateX = 0;
  let blur = 0;
  if (t > 0 && seg.transition !== "cut") {
    const p = interpolate(frame, [0, t], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });
    if (seg.transition === "fade") opacity = p;
    if (seg.transition === "whip") {
      translateX = (1 - p) * 100;
      blur = (1 - p) * 40;
      opacity = Math.min(1, p * 3);
    }
  }
  return (
    <AbsoluteFill style={{ opacity, transform: `translateX(${translateX}%)`, filter: blur ? `blur(${blur}px)` : undefined }}>
      {/* the visual starts playing at the start of the transition window (continuous footage) */}
      <VisualLayer visual={seg.visual} durationFrames={seg.durationFrames + t} />
      {/* overlays see frame 0 at the segment's real start */}
      <Sequence from={t} layout="none">
        <OverlayLayer overlays={seg.overlays} />
      </Sequence>
    </AbsoluteFill>
  );
};

const DipToBlack: React.FC<{ seg: Segment }> = ({ seg }) => {
  const frame = useCurrentFrame();
  const t = Math.max(2, seg.transitionFrames);
  const o = interpolate(frame, [0, t / 2, t], [0, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <AbsoluteFill style={{ background: "black", opacity: o }} />;
};

export const Documentary: React.FC<DocProps> = (props) => {
  const { segments, style, captions } = props;
  return (
    <StyleCtx.Provider value={style}>
      <AbsoluteFill style={{ background: "#000" }}>
        {segments.map((seg) => {
          const from = Math.max(0, seg.startFrame - seg.transitionFrames);
          const dur = seg.durationFrames + (seg.startFrame - from);
          return (
            <Sequence key={seg.id} from={from} durationInFrames={dur} name={seg.id}>
              <SegmentView seg={{ ...seg, transitionFrames: seg.startFrame - from }} />
            </Sequence>
          );
        })}
        {segments
          .filter((s) => s.transition === "dip" && s.transitionFrames > 0)
          .map((seg) => (
            <Sequence key={`dip-${seg.id}`} from={Math.max(0, seg.startFrame - seg.transitionFrames)} durationInFrames={seg.transitionFrames * 2}>
              <DipToBlack seg={{ ...seg, transitionFrames: seg.transitionFrames * 2 }} />
            </Sequence>
          ))}
        <Vignette amount={style.vignette} />
        <Grain amount={style.grain} />
        {captions.enabled ? <Captions words={captions.words} /> : null}
      </AbsoluteFill>
    </StyleCtx.Provider>
  );
};
