---
name: voice-generate
description: Step 2 of video generation - generate voice audio for each step using ChatTTS
---

# Step 2: Voice Audio Generation

This is the second step of the video generation pipeline. It reads `steps.json` from Step 1 and generates a WAV audio file for each step using the ChatTTS script.

## Prerequisites

- `steps.json` must exist in the working directory (produced by Step 1)

## Environment Setup (Must Do First)

Before generating any audio, initialize the Python virtual environment and install dependencies:

```bash
# 1. Create venv (skip if .venv already exists)
python3 -m venv .venv

# 2. Install dependencies from requirements.txt
.venv/bin/pip install -r requirements.txt
```

The `requirements.txt` is at the skill root and includes: ChatTTS, numpy, torch, requests.

If `.venv` already exists and packages are installed, you can skip this step.

## How It Works

For each step across all sections in `steps.json`, run the TTS script:

```bash
.venv/bin/python script/script.py man "<text>" <output_path>
```

### Arguments

- `voice_seed`: Always use `"man"` as the voice seed for consistent male narrator voice.
- `text`: The `text` value from the step. Quote it properly to handle special characters.
- `output_path`: Path for the output WAV file.

### Output File Naming

Save WAV files in an `audio/` subdirectory of the working directory, named by step number:

```
audio/step_1.wav
audio/step_2.wav
audio/step_3.wav
...
```

Use zero-padded numbers if there are 10+ steps (e.g., `step_01.wav`) for proper sorting.

## Execution Pattern

Iterate through sections in order, then steps within each section. Process sequentially (ChatTTS loads large models, parallel execution may cause memory issues):

```bash
# Section 1, steps 1-3:
.venv/bin/python script/script.py man "你知道吗，人工智能其实已经在悄悄改变我们的生活了。" ./audio/step_1.wav
.venv/bin/python script/script.py man "从看病就医到学校教育，AI 的应用可以说无处不在。" ./audio/step_2.wav
.venv/bin/python script/script.py man "根据最新的数据，2024年全球 AI 市场的规模已经超过了5000亿美元。" ./audio/step_3.wav

# Section 2, steps 4-5:
.venv/bin/python script/script.py man "不过与此同时，大家也越来越关注 AI 的安全和伦理问题。" ./audio/step_4.wav
.venv/bin/python script/script.py man "各国政府也都在加快制定相关的法规。" ./audio/step_5.wav
```

## Error Handling

- If a step fails, log the error and continue with remaining steps
- After all steps, report which steps succeeded and which failed
- The script prints the output path on success

## Notes

- Each WAV file is mono, 24kHz, 16-bit PCM
- The script handles mixed Chinese/English text and normalizes technical terms
- Long text is automatically split into segments with pauses between them
- First invocation loads models (~300MB), subsequent calls are faster
