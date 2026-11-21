import React from "react";
import { Composition } from "remotion";
import { Documentary } from "./Documentary";
import type { DocProps } from "./types";

const sample: DocProps = {
  fps: 30,
  width: 1920,
  height: 1080,
  totalFrames: 300,
  title: "Exemple",
  style: { accent: "#E8B04B", text: "#F5F1E8", headingFont: "PlayfairDisplay", bodyFont: "Inter", grain: 0.35, vignette: 0.5 },
  segments: [
    {
      id: "s1",
      startFrame: 0,
      durationFrames: 150,
      transition: "cut",
      transitionFrames: 0,
      visual: { type: "title", title: "Titre du documentaire", subtitle: "Une enquête en images" },
      overlays: [],
    },
    {
      id: "s2",
      startFrame: 150,
      durationFrames: 150,
      transition: "fade",
      transitionFrames: 15,
      visual: { type: "chapter", number: 1, title: "Les origines" },
      overlays: [{ type: "stat", fromFrames: 30, durationFrames: 110, value: 1969, label: "année du premier pas", decimals: 0 }],
    },
  ],
  captions: { enabled: false, words: [] },
  chapterMarks: [{ frame: 150, title: "Les origines" }],
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Documentary"
    component={Documentary}
    defaultProps={sample}
    durationInFrames={sample.totalFrames}
    fps={sample.fps}
    width={sample.width}
    height={sample.height}
    calculateMetadata={({ props }) => ({
      durationInFrames: Math.max(1, props.totalFrames),
      fps: props.fps,
      width: props.width,
      height: props.height,
    })}
  />
);
