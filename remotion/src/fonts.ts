import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadPlayfair } from "@remotion/google-fonts/PlayfairDisplay";
import { loadFont as loadOswald } from "@remotion/google-fonts/Oswald";
import type { Style } from "./types";

const inter = loadInter("normal", { weights: ["400", "600", "800"], subsets: ["latin", "latin-ext"] });
const playfair = loadPlayfair("normal", { weights: ["600", "800"], subsets: ["latin", "latin-ext"] });
const oswald = loadOswald("normal", { weights: ["500", "700"], subsets: ["latin", "latin-ext"] });

export const fontFamilies = {
  Inter: inter.fontFamily,
  PlayfairDisplay: playfair.fontFamily,
  Oswald: oswald.fontFamily,
};

export const headingFont = (s: Style) => fontFamilies[s.headingFont] ?? fontFamilies.PlayfairDisplay;
export const bodyFont = (_s: Style) => fontFamilies.Inter;
