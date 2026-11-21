import React from "react";
import { AbsoluteFill, Easing, Img, interpolate, OffthreadVideo, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import type { Fit, Grade, Motion, Visual } from "../types";
import { useStyle } from "../Documentary";
import { bodyFont, headingFont } from "../fonts";

// ---------- camera motion (Ken Burns / drift) ----------
const motionTransform = (motion: Motion | undefined, p: number, frame: number): string => {
  const e = Easing.inOut(Easing.sin)(p);
  switch (motion) {
    case "zoom-in":
      return `scale(${1.04 + 0.1 * e})`;
    case "zoom-out":
      return `scale(${1.14 - 0.1 * e})`;
    case "pan-left":
      return `scale(1.12) translateX(${3 - 6 * e}%)`;
    case "pan-right":
      return `scale(1.12) translateX(${-3 + 6 * e}%)`;
    case "pan-up":
      return `scale(1.12) translateY(${3 - 6 * e}%)`;
    case "pan-down":
      return `scale(1.12) translateY(${-3 + 6 * e}%)`;
    case "drift":
      return `scale(${1.06 + 0.03 * e}) translate(${Math.sin(frame / 90) * 0.8}%, ${Math.cos(frame / 110) * 0.6}%)`;
    case "static":
    default:
      return "scale(1.0)";
  }
};

const gradeFilter = (g: Grade | undefined): string => {
  switch (g) {
    case "cinematic":
      return "contrast(1.08) saturate(0.88) brightness(0.96)";
    case "warm":
      return "contrast(1.05) saturate(1.05) sepia(0.15) brightness(1.0)";
    case "cold":
      return "contrast(1.06) saturate(0.8) hue-rotate(-8deg) brightness(0.97)";
    case "bw":
      return "grayscale(1) contrast(1.18) brightness(0.98)";
    case "archive":
      return "grayscale(0.55) sepia(0.35) contrast(1.12) brightness(0.95)";
    default:
      return "none";
  }
};

const GradeTint: React.FC<{ grade?: Grade }> = ({ grade }) => {
  if (grade === "cinematic")
    return (
      <AbsoluteFill
        style={{ background: "linear-gradient(180deg, rgba(0,60,80,0.18), rgba(255,140,40,0.10))", mixBlendMode: "soft-light" }}
      />
    );
  if (grade === "cold") return <AbsoluteFill style={{ background: "rgba(30,80,140,0.16)", mixBlendMode: "soft-light" }} />;
  if (grade === "warm") return <AbsoluteFill style={{ background: "rgba(255,150,60,0.12)", mixBlendMode: "soft-light" }} />;
  return null;
};

type MediaProps = {
  kind: "video" | "image";
  src: string;
  trimBeforeFrames?: number;
  playbackRate?: number;
  motion?: Motion;
  grade?: Grade;
  fit?: Fit;
  durationFrames: number;
};

const MediaEl: React.FC<{ p: MediaProps; objectFit: "cover" | "contain"; style?: React.CSSProperties }> = ({ p, objectFit, style }) => {
  const common: React.CSSProperties = { width: "100%", height: "100%", objectFit, ...style };
  if (p.kind === "image") return <Img src={staticFile(p.src)} style={common} />;
  return (
    <OffthreadVideo
      src={staticFile(p.src)}
      trimBefore={Math.max(0, Math.round(p.trimBeforeFrames ?? 0))}
      playbackRate={p.playbackRate ?? 1}
      muted // audio is mixed separately by scripts/render.py (ffmpeg)
      style={common}
    />
  );
};

export const Media: React.FC<MediaProps> = (p) => {
  const frame = useCurrentFrame();
  const prog = Math.min(1, frame / Math.max(1, p.durationFrames));
  const transform = motionTransform(p.motion, prog, frame);
  const filter = gradeFilter(p.grade);
  const fit = p.fit ?? "cover";
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#000" }}>
      {fit === "blur-fill" ? (
        <AbsoluteFill style={{ transform: "scale(1.2)", filter: `blur(40px) brightness(0.45) ${filter === "none" ? "" : filter}` }}>
          <MediaEl p={p} objectFit="cover" />
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill style={{ transform, filter }}>
        <MediaEl p={p} objectFit={fit === "cover" ? "cover" : "contain"} />
      </AbsoluteFill>
      <GradeTint grade={p.grade} />
    </AbsoluteFill>
  );
};

const Letterbox: React.FC = () => {
  const { height } = useVideoConfig();
  const bar = Math.round(height * 0.075);
  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: bar, background: "#000" }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: bar, background: "#000" }} />
    </AbsoluteFill>
  );
};

// ---------- full-screen motion cards ----------
const Backdrop: React.FC<{ bg?: Visual; durationFrames: number; dim?: number }> = ({ bg, durationFrames, dim = 0.55 }) => (
  <AbsoluteFill style={{ background: "radial-gradient(ellipse at 50% 40%, #1c1a17 0%, #070707 75%)" }}>
    {bg ? (
      <AbsoluteFill style={{ filter: "blur(6px)" }}>
        <VisualLayer visual={bg} durationFrames={durationFrames} />
      </AbsoluteFill>
    ) : null}
    <AbsoluteFill style={{ background: `rgba(0,0,0,${bg ? dim : 0})` }} />
  </AbsoluteFill>
);

const TitleCard: React.FC<{ title: string; subtitle?: string; bg?: Visual; durationFrames: number }> = ({ title, subtitle, bg, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = useStyle();
  const inP = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 40 });
  const outP = interpolate(frame, [durationFrames - 15, durationFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const line = interpolate(frame, [10, 45], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <AbsoluteFill>
      <Backdrop bg={bg} durationFrames={durationFrames} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", opacity: outP, textAlign: "center", padding: "0 10%" }}>
        <div
          style={{
            fontFamily: headingFont(s),
            fontWeight: 800,
            fontSize: 118,
            lineHeight: 1.05,
            color: s.text,
            letterSpacing: 1,
            opacity: inP,
            transform: `translateY(${(1 - inP) * 30}px)`,
            textShadow: "0 6px 40px rgba(0,0,0,0.6)",
          }}
        >
          {title}
        </div>
        <div style={{ width: `${line * 260}px`, height: 4, background: s.accent, margin: "34px auto" }} />
        {subtitle ? (
          <div
            style={{
              fontFamily: bodyFont(s),
              fontSize: 40,
              letterSpacing: 8,
              textTransform: "uppercase",
              color: s.text,
              opacity: interpolate(frame, [25, 55], [0, 0.85], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
            }}
          >
            {subtitle}
          </div>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const ChapterCard: React.FC<{ number: number; title: string; bg?: Visual; durationFrames: number }> = ({ number, title, bg, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = useStyle();
  const p = spring({ frame, fps, config: { damping: 200 }, durationInFrames: 35 });
  const outP = interpolate(frame, [durationFrames - 12, durationFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <AbsoluteFill>
      <Backdrop bg={bg} durationFrames={durationFrames} dim={0.65} />
      <AbsoluteFill style={{ justifyContent: "center", paddingLeft: "12%", opacity: outP }}>
        <div style={{ fontFamily: bodyFont(s), fontWeight: 600, fontSize: 34, letterSpacing: 10, color: s.accent, opacity: p }}>
          CHAPITRE {String(number).padStart(2, "0")}
        </div>
        <div
          style={{
            fontFamily: headingFont(s),
            fontWeight: 800,
            fontSize: 104,
            color: s.text,
            marginTop: 18,
            maxWidth: "75%",
            clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`,
          }}
        >
          {title}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const QuoteCard: React.FC<{ text: string; author?: string; bg?: Visual; durationFrames: number }> = ({ text, author, bg, durationFrames }) => {
  const frame = useCurrentFrame();
  const s = useStyle();
  const words = text.split(/\s+/);
  const perWord = Math.max(1, Math.min(6, (durationFrames * 0.5) / words.length));
  return (
    <AbsoluteFill>
      <Backdrop bg={bg} durationFrames={durationFrames} dim={0.7} />
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: "0 14%" }}>
        <div style={{ fontFamily: headingFont(s), fontSize: 180, color: s.accent, lineHeight: 0.6, height: 90 }}>“</div>
        <div style={{ fontFamily: headingFont(s), fontWeight: 600, fontSize: 64, lineHeight: 1.3, color: s.text, textAlign: "center" }}>
          {words.map((w, i) => (
            <span key={i} style={{ opacity: interpolate(frame, [i * perWord, i * perWord + 8], [0.12, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
              {w}{" "}
            </span>
          ))}
        </div>
        {author ? (
          <div style={{ fontFamily: bodyFont(s), fontSize: 32, letterSpacing: 4, color: s.accent, marginTop: 40, textTransform: "uppercase" }}>— {author}</div>
        ) : null}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const MapCard: React.FC<{ src: string; pins: { x: number; y: number; label: string; atFrames?: number }[]; durationFrames: number }> = ({ src, pins, durationFrames }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = useStyle();
  const target = pins[0] ?? { x: 50, y: 50 };
  const z = interpolate(frame, [0, durationFrames], [1.0, 1.35], { extrapolateRight: "clamp", easing: Easing.inOut(Easing.sin) });
  return (
    <AbsoluteFill style={{ overflow: "hidden", background: "#0b0c0e" }}>
      <AbsoluteFill style={{ transform: `scale(${z})`, transformOrigin: `${target.x}% ${target.y}%` }}>
        <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: "saturate(0.6) brightness(0.8) contrast(1.1)" }} />
        {pins.map((pin, i) => {
          const at = pin.atFrames ?? 15 + i * 25;
          const p = spring({ frame: frame - at, fps, config: { damping: 12 } });
          const pulse = ((frame - at) % 45) / 45;
          return (
            <div key={i} style={{ position: "absolute", left: `${pin.x}%`, top: `${pin.y}%`, transform: "translate(-50%,-50%)" }}>
              <div style={{ position: "absolute", width: 90, height: 90, left: -45, top: -45, borderRadius: "50%", border: `3px solid ${s.accent}`, opacity: frame > at ? 1 - pulse : 0, transform: `scale(${0.3 + pulse})` }} />
              <div style={{ width: 22, height: 22, marginLeft: -11, marginTop: -11, borderRadius: "50%", background: s.accent, transform: `scale(${p})`, boxShadow: "0 0 20px rgba(0,0,0,0.6)" }} />
              <div style={{ position: "absolute", left: 24, top: -26, whiteSpace: "nowrap", fontFamily: bodyFont(s), fontWeight: 600, fontSize: 36 / z, color: s.text, background: "rgba(0,0,0,0.65)", padding: "6px 14px", opacity: p }}>
                {pin.label}
              </div>
            </div>
          );
        })}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const TimelineCard: React.FC<{ events: { year: string; label: string }[]; active?: number; bg?: Visual; durationFrames: number }> = ({ events, active, bg, durationFrames }) => {
  const frame = useCurrentFrame();
  const s = useStyle();
  const draw = interpolate(frame, [0, 40], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const n = Math.max(1, events.length);
  return (
    <AbsoluteFill>
      <Backdrop bg={bg} durationFrames={durationFrames} dim={0.72} />
      <div style={{ position: "absolute", left: "8%", right: "8%", top: "52%", height: 4, background: "rgba(255,255,255,0.25)" }}>
        <div style={{ width: `${draw * 100}%`, height: "100%", background: s.accent }} />
      </div>
      {events.map((ev, i) => {
        const x = 8 + (84 * (i + 0.5)) / n;
        const appear = interpolate(frame, [10 + i * 12, 25 + i * 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const isActive = active === undefined || active === i;
        return (
          <div key={i} style={{ position: "absolute", left: `${x}%`, top: "52%", transform: "translate(-50%,-50%)", opacity: appear * (isActive ? 1 : 0.45), textAlign: "center" }}>
            <div style={{ width: isActive ? 26 : 16, height: isActive ? 26 : 16, borderRadius: "50%", background: isActive ? s.accent : s.text, margin: "0 auto" }} />
            <div style={{ position: "absolute", bottom: 46, left: "50%", transform: "translateX(-50%)", fontFamily: headingFont(s), fontWeight: 800, fontSize: isActive ? 64 : 44, color: s.text }}>{ev.year}</div>
            <div style={{ position: "absolute", top: 46, left: "50%", transform: "translateX(-50%)", width: 300, fontFamily: bodyFont(s), fontSize: 28, color: s.text, opacity: 0.9 }}>{ev.label}</div>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

export const VisualLayer: React.FC<{ visual: Visual; durationFrames: number }> = ({ visual, durationFrames }) => {
  switch (visual.type) {
    case "video":
      return (
        <AbsoluteFill>
          <Media kind="video" src={visual.src} trimBeforeFrames={visual.trimBeforeFrames} playbackRate={visual.playbackRate} motion={visual.motion} grade={visual.grade} fit={visual.fit} durationFrames={durationFrames} />
          {visual.letterbox ? <Letterbox /> : null}
        </AbsoluteFill>
      );
    case "image":
      return <Media kind="image" src={visual.src} motion={visual.motion ?? "zoom-in"} grade={visual.grade} fit={visual.fit} durationFrames={durationFrames} />;
    case "color":
      return <AbsoluteFill style={{ background: visual.color ?? "#000" }} />;
    case "title":
      return <TitleCard title={visual.title} subtitle={visual.subtitle} bg={visual.bg} durationFrames={durationFrames} />;
    case "chapter":
      return <ChapterCard number={visual.number} title={visual.title} bg={visual.bg} durationFrames={durationFrames} />;
    case "quote":
      return <QuoteCard text={visual.text} author={visual.author} bg={visual.bg} durationFrames={durationFrames} />;
    case "map":
      return <MapCard src={visual.src} pins={visual.pins} durationFrames={durationFrames} />;
    case "timeline":
      return <TimelineCard events={visual.events} active={visual.active} bg={visual.bg} durationFrames={durationFrames} />;
    default:
      return null;
  }
};
