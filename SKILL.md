---
name: voiceclone
description: Generate speech audio from text using ChatTTS. Use when the user wants to convert text to speech, generate voice audio, create TTS output, or says "voiceclone", "generate voice", "text to speech", "TTS".
---

# VoiceClone - Text to Speech Generator

Generate speech audio from text using ChatTTS.

## Script Location

`script/script.py`

## Usage

```bash
./.venv/bin/python script/script.py <voice_kind> <text> [output_path]
```

**Arguments:**
- `voice_kind`: Voice selector. Use a number or name for a deterministic voice.
- `text`: Text to read aloud.
- `output_path`: (Optional) Output .wav path or directory. Defaults to `~/VoiceCloneResult/output.wav`.

## Default Output

Default output directory: `~/VoiceCloneResult/`
If no output path is specified, the audio will be saved to `~/VoiceCloneResult/output.wav`.

## Examples

```bash
# Generate with a numeric voice kind
./.venv/bin/python script/script.py 1 "Hello, this is a test."

# Generate with a named voice kind
./.venv/bin/python script/script.py "female_voice" "你好世界"

# Generate to a specific path
./.venv/bin/python script/script.py 1 "Hello" ~/Desktop/my_audio.wav

# Generate to a specific directory (will create output.wav in that directory)
./.venv/bin/python script/script.py 1 "Hello" ~/Desktop/
```

## Features

- Uses ChatTTS for text-to-speech generation
- Supports mixed Chinese and English text
- Automatically normalizes technical terms (AI, API, CPU, etc.)
- Splits long text into segments for better TTS quality
- Default output directory: `~/VoiceCloneResult/`
