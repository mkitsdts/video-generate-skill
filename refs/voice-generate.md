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
# 1. Create venv (skip if venv or .venv already exists)
python3 -m venv venv

# 2. Install dependencies from requirements.txt
venv/bin/pip install -r requirements.txt
```

The `requirements.txt` is at the skill root and includes: ChatTTS, numpy, torch, requests.

If `venv` or virtual python env already exists and packages are installed, you can skip this step.

## How It Works

Use the **batch script** to generate all WAV files in one command. It reads `steps.json`, loads the ChatTTS model once, and produces one WAV per step sequentially.

```bash
venv/bin/python scripts/batch_voice.py steps.json [output_dir] [--voice 2422]
```

### Arguments

| Argument | Required | Default | Description |
|---|---|---|---|
| `steps_json` | yes | - | Path to `steps.json` from Step 1 |
| `output_dir` | no | `audio` | Directory for output WAV files |
| `--voice` | no | `2422` | Voice seed for ChatTTS |

### Output File Naming

WAV files are saved in the output directory, named by step number with zero-padded digits:

```
audio/step_1.wav
audio/step_2.wav
...
audio/step_09.wav
audio/step_10.wav
```

### Example

```bash
venv/bin/python scripts/batch_voice.py steps.json ./audio --voice 2422
```

Output:

```
Loading ChatTTS models (first invocation is slow)...
[1/5] step_1.wav: 你知道吗，人工智能其实已经在悄悄改变...
  -> audio/step_1.wav  (3.2s)
[2/5] step_2.wav: 从看病就医到学校教育，AI 的应用可以说...
  -> audio/step_2.wav  (2.8s)
...
Done. 5/5 succeeded.
```

### Single Step (Manual)

If you need to regenerate a single step, use `script.py` directly:

```bash
venv/bin/python scripts/script.py 2422 "<text>" <output_path>
```

## Error Handling

### steps.json Validation (Before Generation Starts)

The script validates `steps.json` strictly before doing any work. If any check fails, it prints an error to stderr and exits with code 1 immediately:

- File not found or unreadable
- Invalid JSON syntax
- Root element is not a JSON array
- Section object missing `section` or `steps` field
- `steps` is not an array
- Step object missing `step` or `text` field
- `step` is not a positive integer
- `text` is empty or not a string
- Duplicate step numbers
- Step numbers not sequential from 1 to N

### Generation Errors

- If a step fails during TTS generation, the script logs the error and continues with remaining steps
- At the end, a summary is printed: how many succeeded and the list of failed step numbers
- Exit code is `1` if any step failed, `0` if all succeeded

## Notes

- The batch script loads the ChatTTS model only once (~300MB), making it much faster than calling `script.py` per step
- Each WAV file is mono, 24kHz, 16-bit PCM
- The script handles mixed Chinese/English text and normalizes technical terms
- Long text is automatically split into segments with pauses between them
- Steps are processed sequentially — parallel execution may cause memory issues
