---
name: subtitle-generate
description: Step 3 of video generation - generate SRT subtitle file from steps.json and audio durations
---

# Step 3: SRT Subtitle Generation

This step reads `steps.json` from Step 1 and the audio files from Step 2 to produce an SRT subtitle file with accurate timestamps.

## Prerequisites

- `steps.json` exists (from Step 1)
- `audio/step_*.wav` files exist (from Step 2)

## How It Works

Write a Python script `scripts/gen_subtitle.py` that:

1. Parses `steps.json` to extract each step's text content
2. Reads each audio file (`audio/step_N.wav`) using the `wave` module to get its duration
3. Calculates cumulative timestamps based on audio durations
4. Outputs a standard SRT file

## Script: `scripts/gen_subtitle.py`

## Usage

```bash
# Default: reads steps.json, audio/ dir, outputs subtitle.srt
python scripts/gen_subtitle.py steps.json

# Custom paths
python scripts/gen_subtitle.py steps.json ./audio ./output.srt
```

## Output

A standard SRT file like:

```srt
1
00:00:00,000 --> 00:00:03,200
你知道吗，人工智能其实已经在悄悄改变我们的生活了。

2
00:00:03,500 --> 00:00:06,300
从看病就医到学校教育，AI 的应用可以说无处不在。

3
00:00:06,600 --> 00:00:12,100
根据最新的数据，2024年全球 AI 市场的规模已经超过了5000亿美元，这个数字真的很惊人。
```

## Notes

- The `gap` parameter (default 0.3s) adds a small pause between subtitle entries for readability
- Audio file lookup supports zero-padded step numbers (e.g., `step_01.wav` or `step_001.wav`)
- The SRT file uses UTF-8 encoding to support Chinese and other Unicode text
- The script uses the standard `wave` module — no additional dependencies needed
