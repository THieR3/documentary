// Shape of build/props.json, produced by scripts/build_props.py from timeline.json.
// All times here are already in FRAMES (global or segment-relative as noted).

export type Motion =
  | "static"
  | "zoom-in"
  | "zoom-out"
  | "pan-left"
  | "pan-right"
  | "pan-up"
  | "pan-down"
  | "drift";

export type Grade = "none" | "cinematic" | "warm" | "cold" | "bw" | "archive";

export type Fit = "cover" | "contain" | "blur-fill";

export type Transition = "cut" | "fade" | "dip" | "whip";

export type Visual =
  | {
      type: "video";
      src: string; // relative to the project's media/ dir
      trimBeforeFrames: number; // where to start in the source
      playbackRate?: number;
      motion?: Motion;
      grade?: Grade;
      fit?: Fit;
      letterbox?: boolean;
    }
  | { type: "image"; src: string; motion?: Motion; grade?: Grade; fit?: Fit }
  | { type: "color"; color?: string }
  | { type: "title"; title: string; subtitle?: string; bg?: Visual }
  | { type: "chapter"; number: number; title: string; bg?: Visual }
  | { type: "quote"; text: string; author?: string; bg?: Visual }
  | { type: "map"; src: string; pins: MapPin[]; bg?: undefined }
  | { type: "timeline"; events: TimelineEvent[]; active?: number; bg?: Visual };

export type MapPin = { x: number; y: number; label: string; atFrames?: number };
export type TimelineEvent = { year: string; label: string };

export type Overlay = { fromFrames: number; durationFrames: number } & (
  | { type: "lowerThird"; title: string; subtitle?: string }
  | { type: "credit"; text: string }
  | { type: "stat"; value: number; prefix?: string; suffix?: string; label: string; decimals?: number; position?: "center" | "left" | "right" }
  | { type: "kinetic"; lines: string[] }
  | { type: "highlight"; box: [number, number, number, number]; label?: string; shape?: "rect" | "circle" }
  | { type: "quote"; text: string; author?: string }
  | { type: "date"; text: string }
);

export type Segment = {
  id: string;
  startFrame: number;
  durationFrames: number;
  transition: Transition;
  transitionFrames: number;
  visual: Visual;
  overlays: Overlay[];
};

export type CaptionWord = { text: string; start: number; end: number }; // global frames

export type Style = {
  accent: string;
  text: string;
  headingFont: "PlayfairDisplay" | "Oswald" | "Inter";
  bodyFont: "Inter";
  grain: number; // 0..1
  vignette: number; // 0..1
};

export type DocProps = {
  fps: number;
  width: number;
  height: number;
  totalFrames: number;
  title: string;
  style: Style;
  segments: Segment[];
  captions: { enabled: boolean; words: CaptionWord[] };
  chapterMarks: { frame: number; title: string }[];
};
