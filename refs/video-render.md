---
name: video-render
description: Step 3 of video generation - create Remotion React code and render final video with audio
---

# Step 3: Video Rendering with Remotion

This is the third and final step. It takes the audio files from Step 2 and the section/step data from Step 1, creates a Remotion React project, and renders the final video.

## Prerequisites

- `steps.json` exists (from Step 1) — contains sections with nested steps
- `audio/step_*.wav` files exist (from Step 2)
- Node.js and npm are available

## Key Concept: Section vs Step

- **Section** = one visual page (like a PPT slide). The background and layout stay the same for all steps in the section.
- **Step** = one spoken sentence within a section. Audio plays sequentially. The displayed text updates as each step starts.

```
Section 1 page shows on screen
  ├── step 1 audio plays, text shows step 1
  ├── step 2 audio plays, text updates to step 2
  └── step 3 audio plays, text updates to step 3
Section 2 page shows (new background/layout)
  ├── step 4 audio plays, text shows step 4
  └── step 5 audio plays, text updates to step 5
```

## Overview

1. Create a Remotion project in a `video/` subdirectory of the working directory
2. Write a React component with section-based pages and step-based audio/text
3. Render the video to MP4

## Step-by-Step

### 3.1 Initialize Remotion Project

```bash
cd <working_dir>/video
npx create-video@latest --template blank
npm install
```

### 3.2 Get Audio Durations

Before writing the composition, measure each audio file's duration:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 audio/step_1.wav
```

Store durations alongside step data - you'll need them for frame calculations.

### 3.3 Write the Composition

Create `src/Root.tsx` (or equivalent) with this structure:

```tsx
import { Composition } from "remotion";
import { VideoComposition } from "./Composition";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="MainVideo"
      component={VideoComposition}
      durationInFrames={totalFrames}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
```

### 3.4 Write the Main Component

`src/Composition.tsx` — the core video component. Each section is a visual page; steps within share the page and play audio sequentially.

```tsx
import { Audio, Sequence, useCurrentFrame, staticFile, interpolate } from "remotion";

interface Step {
  step: number;
  text: string;
  durationInFrames: number;
  startFrame: number;
}

interface Section {
  section: number;
  steps: Step[];
  startFrame: number;
  durationInFrames: number;
}

const StepText: React.FC<{ text: string; durationInFrames: number }> = ({ text, durationInFrames }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div style={{ opacity, fontSize: 30, color: "white", textAlign: "center", padding: "0 120px" }}>
      {text}
    </div>
  );
};

export const VideoComposition: React.FC = () => {
  const sections: Section[] = [
    // Populated from steps.json + audio durations
  ];

  return (
    <div style={{ backgroundColor: "#1a1a2e", width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
      {sections.map((sec) => (
        <Sequence key={sec.section} from={sec.startFrame} durationInFrames={sec.durationInFrames}>
          {/* Section background — stays the same for all steps */}
          <div style={{ position: "absolute", width: "100%", height: "100%" }}>
            {sec.steps.map((s) => (
              <Sequence key={s.step} from={s.startFrame - sec.startFrame} durationInFrames={s.durationInFrames}>
                <StepText text={s.text} durationInFrames={s.durationInFrames} />
                <Audio src={staticFile(`audio/step_${s.step}.wav`)} />
              </Sequence>
            ))}
          </div>
        </Sequence>
      ))}
    </div>
  );
};
```

### 3.5 Design the Visual Layout

Each section page should display:
- **Background**: solid color or gradient — stays the same for all steps in the section
- **Section visual diagram** (REQUIRED): a dedicated illustration/diagram for the section — see Section 3.5.1
- **Text (subtitle)**: centered, small font (28-32px), good contrast — updates when the next step starts. Subtle, bottom-aligned.
- **Section indicator**: optional small section number or progress bar
- **Animations**: fade-in text when each step starts using `useCurrentFrame()` and `interpolate()`

Recommended base style:
- Resolution: 1920x1080 (16:9)
- FPS: 30
- Background: dark (#1a1a2e or similar)
- Text (subtitle): white or light color, 28-32px font size — small and at the bottom, NOT the main focus
- Padding: generous margins for readability
- Layout: visual diagram takes top 80-85% of frame, text takes bottom 15-20%
- The visual diagram is the PRIMARY element — users must clearly see it
- Subtitles are secondary — small, bottom-aligned, just for reading along

#### 3.5.1 Section Visual Diagrams (REQUIRED)

Each section MUST have a visual diagram/illustration that matches its content. This is not optional.

**Requirements:**
1. **Content match**: The visual MUST accurately represent the concept discussed in that section. Read the step texts carefully and design a diagram that illustrates the key idea.
2. **Minimum size**: The visual diagram MUST occupy at least 80% of the frame height (top portion). This is the PRIMARY element users should see — make it large and clear.
3. **Readability**: All labels, icons, and diagram elements must be clearly visible at 1920x1080. Use minimum 22px font for labels, 28px+ for node/box text. Diagram elements should be large enough to read easily.
4. **Consistent style**: Use a unified color scheme and design language across all sections.
5. **Animation**: Diagram elements should fade in with staggered delays using `useCurrentFrame()` and `interpolate()`.

**How to create visuals:**
- Create a separate `SectionVisuals.tsx` file with one component per section
- Use CSS + inline styles for diagrams (boxes, arrows, flow charts, tables, bar charts)
- Use a `sectionVisualMap: Record<number, React.FC>` to map section numbers to visual components
- Import and render the appropriate visual in `Composition.tsx` based on `sec.section`

**Common diagram types by content:**
- Architecture/system diagrams: boxes + connecting arrows (e.g., coordinator → participants)
- Flow/sequence diagrams: horizontal or vertical step flows with arrows
- Comparison tables: grid layout with colored headers
- Bar charts: horizontal bars for metrics/performance data
- Decision trees: branching paths for yes/no scenarios
- Role diagrams: labeled boxes for different components/actors

**Example layout in Composition.tsx:**
```tsx
<div style={{ display: "flex", flexDirection: "column", width: "100%", height: "100%" }}>
  {/* Visual diagram - top 85% — PRIMARY element */}
  <div style={{ flex: "0 0 85%", display: "flex", alignItems: "center", justifyContent: "center" }}>
    {Visual && <Visual />}
  </div>
  {/* Text subtitle - bottom 15% — small, secondary */}
  <div style={{ flex: "0 0 15%", display: "flex", alignItems: "center", justifyContent: "center", padding: "0 120px" }}>
    {/* StepText with 28-32px font + Audio sequences */}
  </div>
</div>
```

### 3.6 Copy Audio Files

Copy the `audio/` directory into Remotion's `public/` folder so `staticFile()` can reference them:

```bash
cp -r ../audio video/public/audio
```

### 3.7 Calculate Frames

For each step:
- `step.durationInFrames = Math.ceil(audioDurationSeconds * fps)`
- Add a small buffer (15-30 frames / 0.5-1s) after each step for breathing room

For each section:
- `section.durationInFrames` = sum of all its steps' durations
- `section.startFrame` = sum of all previous sections' durations

Total video frames = sum of all sections' durations.

### 3.8 Render

```bash
cd <working_dir>/video
npx remotion render MainVideo ../output.mp4
```

Output the final MP4 to the working directory root.

## File Structure After Completion

```
<working_dir>/
├── steps.json          # Step 1 output
├── audio/              # Step 2 output
│   ├── step_1.wav
│   ├── step_2.wav
│   └── ...
├── video/              # Remotion project
│   ├── src/
│   │   ├── Root.tsx
│   │   ├── Composition.tsx
│   │   └── ...
│   ├── public/
│   │   └── audio/      # Copied from audio/
│   └── package.json
└── output.mp4          # Final video
```

## Troubleshooting

- If Remotion fails to find audio files, verify they are in `video/public/audio/`
- If text is too long for the frame, reduce font size or split into more steps
- If rendering is slow, try lower resolution (1280x720) or fewer FPS (24)
