---
name: videogen
description: Generate videos from text scripts. Converts written scripts into narrated videos by splitting text into steps, generating voice audio with ChatTTS, and rendering with Remotion. Use when the user wants to "make a video from text", "generate video", "text to video", "script to video", or says "videogen".
---

# VideoGen - Text to Video Generator

Convert a text script into a narrated video through a 3-step pipeline.

## Pipeline Overview

```
User Script
    │
    ▼
┌─────────────────────┐
│ Step 1: Script Split │  refs/script-split.md
│ Split & oral convert │
│ Output: steps.json   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 2: Voice Gen    │  refs/voice-generate.md
│ ChatTTS per step     │
│ Output: audio/*.wav  │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Step 3: Video Render │  refs/video-render.md
│ Remotion React code  │
│ Output: output.mp4   │
└─────────────────────┘
```

## How to Use

When the user provides a script/text to convert into video, execute the three steps in order. Load each step's ref document **only when starting that step** (progressive loading).

1. **Before Step 1**: Read `refs/script-split.md` for detailed instructions on splitting and oral conversion
2. **Before Step 2**: Read `refs/voice-generate.md` for TTS generation details
3. **Before Step 3**: Read `refs/video-render.md` for Remotion rendering instructions

## Working Directory

All intermediate and final files are created in a working directory. Default: current directory or a user-specified path.

```
<working_dir>/
├── steps.json       # Step 1: structured step plan
├── audio/           # Step 2: WAV files per step
│   ├── step_1.wav
│   └── ...
├── video/           # Step 3: Remotion project
└── output.mp4       # Final video
```

## Quick Reference

### Step 1 - Script Split
- Input: user's raw text/script
- Action: split into **sections** (visual pages) and **steps** (spoken sentences), convert to oral style
- Output: `steps.json` — array of `{section, steps: [{step, text}]}`
- Detail: `refs/script-split.md`

### Step 2 - Voice Generation
- Input: `steps.json`
- Setup: `python3 -m venv venv && venv/bin/pip install -r requirements.txt` (skip if already done)
- Action: run `script/script.py` for each step to generate WAV audio (voice seed fixed as `"man"`)
- Command: `venv/bin/python script/script.py man "<text>" <output_path>`
- Output: `audio/step_N.wav` files
- Detail: `refs/voice-generate.md`

### Step 3 - Video Rendering
- Input: `steps.json` + `audio/*.wav`
- Action: create Remotion React project, sync text display with audio, render MP4
- Output: `output.mp4` in working directory
- Detail: `refs/video-render.md`
