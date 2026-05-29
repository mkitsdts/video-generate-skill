import json
import os
import sys
import wave


def get_wav_duration(filepath: str) -> float:
    """Get duration in seconds of a WAV file."""
    with wave.open(filepath, "r") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        return frames / rate


def format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(
    steps_json_path: str, audio_dir: str, output_path: str, gap: float = 0.3
):
    """
    Generate SRT subtitle file.

    Args:
        steps_json_path: Path to steps.json
        audio_dir: Directory containing step_N.wav files
        output_path: Output SRT file path
        gap: Gap in seconds between consecutive subtitles (default 0.3s)
    """
    with open(steps_json_path, "r", encoding="utf-8") as f:
        sections = json.load(f)

    # Flatten all steps in order
    all_steps = []
    for section in sections:
        for step in section["steps"]:
            all_steps.append(step)

    # Build subtitle entries with timestamps
    entries = []
    current_time = 0.0

    for step in all_steps:
        step_num = step["step"]
        text = step["text"]

        # Find the audio file (zero-padded or not)
        audio_path = None
        for pattern in [
            os.path.join(audio_dir, f"step_{step_num}.wav"),
            os.path.join(audio_dir, f"step_{step_num:02d}.wav"),
            os.path.join(audio_dir, f"step_{step_num:03d}.wav"),
        ]:
            if os.path.exists(pattern):
                audio_path = pattern
                break

        if audio_path is None:
            print(
                f"Warning: audio file not found for step {step_num}, skipping",
                file=sys.stderr,
            )
            continue

        duration = get_wav_duration(audio_path)
        start_time = current_time
        end_time = current_time + duration

        entries.append(
            {
                "index": step_num,
                "start": start_time,
                "end": end_time,
                "text": text,
            }
        )

        current_time = end_time + gap

    # Write SRT file
    with open(output_path, "w", encoding="utf-8") as f:
        for i, entry in enumerate(entries, 1):
            f.write(f"{i}\n")
            f.write(
                f"{format_srt_time(entry['start'])} --> {format_srt_time(entry['end'])}\n"
            )
            f.write(f"{entry['text']}\n")
            f.write("\n")

    print(f"Generated {len(entries)} subtitle entries -> {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gen_subtitle.py <steps.json> [audio_dir] [output.srt]")
        sys.exit(1)

    steps_json = sys.argv[1]
    audio_dir = sys.argv[2] if len(sys.argv) > 2 else "audio"
    output = sys.argv[3] if len(sys.argv) > 3 else "subtitle.srt"

    generate_srt(steps_json, audio_dir, output)
