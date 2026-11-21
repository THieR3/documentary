import React from "react";
import { AbsoluteFill, Easing, interpolate, Sequence, spring, useCurrentFrame, useVideoConfig } from "remotion";
import type { Overlay } from "../types";
import { useStyle } from "../Documentary";
import { bodyFont, headingFont } from "../fonts";

const useInOut = (durationFrames: number, inF = 14, outF = 12) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const inP = spring({ frame, fps, config: { damping: 200 }, durationInFrames: inF * 2 });
  const outP = interpolate(frame, [durationFrames - outF, durationFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { frame, inP, outP, vis: Math.min(inP, outP) };
};

const LowerThird: React.FC<{ title: string; subtitle?: string; d: number }> = ({ title, subtitle, d }) => {
  const s = useStyle();
  const { inP, outP } = useInOut(d);
  return (
    <div style={{ position: "absolute", left: 110, bottom: 150, opacity: outP }}>
      <div style={{ width: 8, height: subtitle ? 118 : 72, background: s.accent, position: "absolute", left: -26, top: 0, transform: `scaleY(${inP})`, transformOrigin: "top" }} />
      <div style={{ clipPath: `inset(0 ${(1 - inP) * 100}% 0 0)` }}>
        <div style={{ fontFamily: bodyFont(s), fontWeight: 800, fontSize: 56, color: s.text, textShadow: "0 3px 18px rgba(0,0,0,0.75)" }}>{title}</div>
        {subtitle ? (
          <div style={{ fontFamily: bodyFont(s), fontWeight: 400, fontSize: 32, color: s.text, opacity: 0.85, marginTop: 6, textShadow: "0 2px 12px rgba(0,0,0,0.8)" }}>{subtitle}</div>
        ) : null}
      </div>
    </div>
  );
};

// Source credit: always shown on borrowed footage ("Archives : …", "Extrait : …").
const Credit: React.FC<{ text: string; d: number }> = ({ text, d }) => {
  const s = useStyle();
  const { vis } = useInOut(d, 10, 10);
  return (
    <div style={{ position: "absolute", right: 70, top: 60, opacity: vis * 0.9, fontFamily: bodyFont(s), fontSize: 24, letterSpacing: 2, color: s.text, textTransform: "uppercase", background: "rgba(0,0,0,0.45)", padding: "8px 16px", borderLeft: `3px solid ${s.accent}` }}>
      {text}
    </div>
  );
};

const DateTag: React.FC<{ text: string; d: number }> = ({ text, d }) => {
  const s = useStyle();
  const { vis, inP } = useInOut(d);
  return (
    <div style={{ position: "absolute", left: 110, top: 90, opacity: vis, fontFamily: headingFont(s), fontWeight: 800, fontSize: 64, color: s.text, letterSpacing: 4, transform: `translateY(${(1 - inP) * -20}px)`, textShadow: "0 4px 24px rgba(0,0,0,0.7)" }}>
      {text}
    </div>
  );
};

const fmt = (n: number, decimals: number) =>
  n.toLocaleString("fr-FR", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });

const Stat: React.FC<{ value: number; prefix?: string; suffix?: string; label: string; decimals?: number; position?: "center" | "left" | "right"; d: number }> = (p) => {
  const s = useStyle();
  const { frame, vis } = useInOut(p.d);
  const count = interpolate(frame, [0, Math.min(45, p.d * 0.6)], [0, p.value], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const pos = p.position ?? "center";
  const align: React.CSSProperties =
    pos === "center" ? { left: 0, right: 0, textAlign: "center", top: "34%" } : pos === "left" ? { left: 110, top: "36%" } : { right: 110, top: "36%", textAlign: "right" };
  return (
    <>
      {pos === "center" ? <AbsoluteFill style={{ background: "rgba(0,0,0,0.45)", opacity: vis }} /> : null}
      <div style={{ position: "absolute", ...align, opacity: vis }}>
        <div style={{ fontFamily: headingFont(s), fontWeight: 800, fontSize: 150, color: s.accent, lineHeight: 1, textShadow: "0 6px 30px rgba(0,0,0,0.6)" }}>
          {p.prefix ?? ""}
          {fmt(count, p.decimals ?? 0)}
          {p.suffix ?? ""}
        </div>
        <div style={{ fontFamily: bodyFont(s), fontWeight: 600, fontSize: 40, color: s.text, marginTop: 14, textTransform: "uppercase", letterSpacing: 4 }}>{p.label}</div>
      </div>
    </>
  );
};

const Kinetic: React.FC<{ lines: string[]; d: number }> = ({ lines, d }) => {
  const s = useStyle();
  const { frame, outP } = useInOut(d);
  const { fps } = useVideoConfig();
  const step = Math.max(8, Math.min(20, (d * 0.6) / Math.max(1, lines.length)));
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", background: `rgba(0,0,0,${0.5 * outP})`, opacity: outP }}>
      {lines.map((l, i) => {
        const p = spring({ frame: frame - i * step, fps, config: { damping: 18, mass: 0.6 } });
        return (
          <div key={i} style={{ fontFamily: headingFont(s), fontWeight: 800, fontSize: i === lines.length - 1 ? 120 : 84, color: i === lines.length - 1 ? s.accent : s.text, opacity: p, transform: `translateY(${(1 - p) * 40}px) scale(${0.9 + 0.1 * p})`, textTransform: "uppercase", letterSpacing: 2 }}>
            {l}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

// Points at something inside the source footage (a person, an object, a detail).
const Highlight: React.FC<{ box: [number, number, number, number]; label?: string; shape?: "rect" | "circle"; d: number }> = ({ box, label, shape, d }) => {
  const s = useStyle();
  const { frame, vis } = useInOut(d);
  const [x, y, w, h] = box; // percent of frame
  const draw = interpolate(frame, [0, 20], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const per = shape === "circle" ? Math.PI * 100 : 400;
  return (
    <AbsoluteFill style={{ opacity: vis }}>
      <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" style={{ position: "absolute" }}>
        <defs>
          <mask id="hl-mask">
            <rect x="0" y="0" width="100" height="100" fill="white" />
            {shape === "circle" ? <ellipse cx={x + w / 2} cy={y + h / 2} rx={w / 2} ry={h / 2} fill="black" /> : <rect x={x} y={y} width={w} height={h} fill="black" />}
          </mask>
        </defs>
        <rect x="0" y="0" width="100" height="100" fill={`rgba(0,0,0,${0.45 * draw})`} mask="url(#hl-mask)" />
        {shape === "circle" ? (
          <ellipse cx={x + w / 2} cy={y + h / 2} rx={w / 2} ry={h / 2} fill="none" stroke={s.accent} strokeWidth={0.35} vectorEffect="non-scaling-stroke" pathLength={per} strokeDasharray={per} strokeDashoffset={per * (1 - draw)} style={{ strokeWidth: 5 }} />
        ) : (
          <rect x={x} y={y} width={w} height={h} fill="none" stroke={s.accent} vectorEffect="non-scaling-stroke" pathLength={per} strokeDasharray={per} strokeDashoffset={per * (1 - draw)} style={{ strokeWidth: 5 }} />
        )}
      </svg>
      {label ? (
        <div style={{ position: "absolute", left: `${x}%`, top: `calc(${y + h}% + 16px)`, fontFamily: bodyFont(s), fontWeight: 600, fontSize: 34, color: "#111", background: s.accent, padding: "6px 14px", opacity: draw }}>
          {label}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

const QuoteOverlay: React.FC<{ text: string; author?: string; d: number }> = ({ text, author, d }) => {
  const s = useStyle();
  const { vis, inP } = useInOut(d);
  return (
    <div style={{ position: "absolute", left: "10%", right: "10%", bottom: 170, textAlign: "center", opacity: vis, transform: `translateY(${(1 - inP) * 20}px)` }}>
      <div style={{ display: "inline-block", background: "rgba(0,0,0,0.6)", padding: "22px 36px", fontFamily: headingFont(s), fontSize: 50, lineHeight: 1.3, color: s.text }}>
        « {text} »
        {author ? <div style={{ fontFamily: bodyFont(s), fontSize: 28, color: s.accent, marginTop: 12, letterSpacing: 3, textTransform: "uppercase" }}>— {author}</div> : null}
      </div>
    </div>
  );
};

const OverlayItem: React.FC<{ o: Overlay }> = ({ o }) => {
  const d = o.durationFrames;
  switch (o.type) {
    case "lowerThird":
      return <LowerThird title={o.title} subtitle={o.subtitle} d={d} />;
    case "credit":
      return <Credit text={o.text} d={d} />;
    case "date":
      return <DateTag text={o.text} d={d} />;
    case "stat":
      return <Stat {...o} d={d} />;
    case "kinetic":
      return <Kinetic lines={o.lines} d={d} />;
    case "highlight":
      return <Highlight box={o.box} label={o.label} shape={o.shape} d={d} />;
    case "quote":
      return <QuoteOverlay text={o.text} author={o.author} d={d} />;
    default:
      return null;
  }
};

export const OverlayLayer: React.FC<{ overlays: Overlay[] }> = ({ overlays }) => (
  <AbsoluteFill>
    {overlays.map((o, i) => (
      <Sequence key={i} from={o.fromFrames} durationInFrames={Math.max(1, o.durationFrames)} layout="none">
        <AbsoluteFill>
          <OverlayItem o={o} />
        </AbsoluteFill>
      </Sequence>
    ))}
  </AbsoluteFill>
);
