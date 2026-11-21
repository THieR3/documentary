import React, { useMemo } from "react";
import { useCurrentFrame } from "remotion";
import type { CaptionWord } from "../types";
import { useStyle } from "../Documentary";
import { bodyFont } from "../fonts";

// Groups words into short lines (max 7 words, breaks on pauses) and highlights the spoken word.
const group = (words: CaptionWord[]) => {
  const out: CaptionWord[][] = [];
  let cur: CaptionWord[] = [];
  words.forEach((w, i) => {
    const prev = words[i - 1];
    const pause = prev ? w.start - prev.end > 12 : false;
    if (cur.length >= 7 || (pause && cur.length) || (prev && /[.!?]$/.test(prev.text) && cur.length)) {
      out.push(cur);
      cur = [];
    }
    cur.push(w);
  });
  if (cur.length) out.push(cur);
  return out;
};

export const Captions: React.FC<{ words: CaptionWord[] }> = ({ words }) => {
  const frame = useCurrentFrame();
  const s = useStyle();
  const groups = useMemo(() => group(words), [words]);
  const g = groups.find((gr) => frame >= gr[0].start && frame <= gr[gr.length - 1].end + 6);
  if (!g) return null;
  return (
    <div style={{ position: "absolute", left: "12%", right: "12%", bottom: 64, textAlign: "center" }}>
      <span style={{ fontFamily: bodyFont(s), fontWeight: 600, fontSize: 42, lineHeight: 1.35, padding: "6px 14px", background: "rgba(0,0,0,0.55)", boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>
        {g.map((w, i) => (
          <span key={i} style={{ color: frame >= w.start && frame <= w.end + 2 ? s.accent : s.text }}>
            {w.text}{" "}
          </span>
        ))}
      </span>
    </div>
  );
};
