"""Batch voice generation: reads steps.json and produces one WAV per step."""

import argparse
import json
import sys
import time
from pathlib import Path

# Reuse core functions from script.py without subprocess overhead.
from script import infer_wav, load_chat, write_wav


def main():
    parser = argparse.ArgumentParser(
        description="Batch-generate WAV audio for every step in steps.json.",
    )
    parser.add_argument(
        "steps_json",
        help="Path to steps.json produced by Step 1.",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="audio",
        help='Output directory for WAV files (default: "audio").',
    )
    parser.add_argument(
        "--voice",
        default="man",
        help='Voice seed for ChatTTS (default: "man").',
    )
    args = parser.parse_args()

    steps_path = Path(args.steps_json)
    if not steps_path.is_file():
        print(f"Error: {steps_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(steps_path, encoding="utf-8") as f:
        try:
            sections = json.load(f)
        except json.JSONDecodeError as exc:
            print(f"Error: Invalid JSON in {steps_path}: {exc}", file=sys.stderr)
            sys.exit(1)

    if not isinstance(sections, list):
        print(f"Error: steps.json root must be a JSON array, got {type(sections).__name__}.", file=sys.stderr)
        sys.exit(1)

    # Collect all steps in order, computing a global sequential number.
    all_steps = []
    for i, section in enumerate(sections):
        if not isinstance(section, dict):
            print(f"Error: section at index {i} must be an object, got {type(section).__name__}.", file=sys.stderr)
            sys.exit(1)
        if "section" not in section:
            print(f"Error: section at index {i} is missing required field 'section'.", file=sys.stderr)
            sys.exit(1)
        if "steps" not in section:
            print(f"Error: section {section['section']} is missing required field 'steps'.", file=sys.stderr)
            sys.exit(1)
        if not isinstance(section["steps"], list):
            print(f"Error: section {section['section']} 'steps' must be an array.", file=sys.stderr)
            sys.exit(1)

        for j, step in enumerate(section["steps"]):
            if not isinstance(step, dict):
                print(f"Error: step at section {section['section']}, index {j} must be an object.", file=sys.stderr)
                sys.exit(1)
            if "step" not in step:
                print(f"Error: step at section {section['section']}, index {j} is missing required field 'step'.", file=sys.stderr)
                sys.exit(1)
            if "text" not in step:
                print(f"Error: step {step['step']} is missing required field 'text'.", file=sys.stderr)
                sys.exit(1)
            if not isinstance(step["step"], int) or step["step"] < 1:
                print(f"Error: step number must be a positive integer, got {step['step']!r}.", file=sys.stderr)
                sys.exit(1)
            if not isinstance(step["text"], str) or not step["text"].strip():
                print(f"Error: step {step['step']} 'text' must be a non-empty string.", file=sys.stderr)
                sys.exit(1)
            all_steps.append(step)

    if not all_steps:
        print("Error: No steps found in steps.json.", file=sys.stderr)
        sys.exit(1)

    # Check for duplicate step numbers.
    seen = set()
    for step in all_steps:
        num = step["step"]
        if num in seen:
            print(f"Error: Duplicate step number {num}.", file=sys.stderr)
            sys.exit(1)
        seen.add(num)

    # Check step numbers are sequential starting from 1.
    expected = list(range(1, len(all_steps) + 1))
    actual = sorted(seen)
    if actual != expected:
        print(f"Error: Step numbers must be sequential from 1 to {len(all_steps)}, got {actual}.", file=sys.stderr)
        sys.exit(1)

    total = len(all_steps)
    pad = len(str(total))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load model once for all steps.
    print("Loading ChatTTS models (first invocation is slow)...")
    chat = load_chat()

    succeeded = []
    failed = []

    for step in all_steps:
        step_num = step["step"]
        text = step["text"]
        filename = f"step_{str(step_num).zfill(pad)}.wav"
        out_path = out_dir / filename

        print(f"[{step_num}/{total}] {filename}: {text[:40]}...")
        start = time.time()
        try:
            wav = infer_wav(chat, args.voice, text)
            write_wav(out_path, wav)
            elapsed = time.time() - start
            print(f"  -> {out_path}  ({elapsed:.1f}s)")
            succeeded.append(step_num)
        except Exception as exc:
            elapsed = time.time() - start
            print(f"  -> FAILED after {elapsed:.1f}s: {exc}", file=sys.stderr)
            failed.append(step_num)

    # Summary
    print(f"\nDone. {len(succeeded)}/{total} succeeded.")
    if failed:
        print(f"Failed steps: {failed}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
