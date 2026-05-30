import argparse
import hashlib
import os
import re
import wave
from pathlib import Path
from typing import Any

import ChatTTS
import numpy as np
import torch

SAMPLE_RATE = 24_000
MAX_SEGMENT_CHARS = 80
SENTENCE_PAUSE_SECONDS = 0.28
TECH_TERM_REPLACEMENTS = {
    "AI": "A I",
    "API": "A P I",
    "CPU": "C P U",
    "CSS": "C S S",
    "GPU": "G P U",
    "HTML": "H T M L",
    "HTTP": "H T T P",
    "HTTPS": "H T T P S",
    "IDE": "I D E",
    "IOS": "i O S",
    "iOS": "i O S",
    "JSON": "J S O N",
    "LLM": "L L M",
    "NLP": "N L P",
    "SQL": "S Q L",
    "UI": "U I",
    "URL": "U R L",
    "USB": "U S B",
    "UX": "U X",
    "XML": "X M L",
}


def resolve_output_path(output_path):
    if output_path is None:
        return Path.home() / "VoiceCloneResult" / "output.wav"

    value = str(output_path).strip()
    if value == "" or value.lower() in {"none", "null"}:
        return Path.home() / "VoiceCloneResult" / "output.wav"

    path = Path(value).expanduser()
    if path.suffix.lower() != ".wav":
        path = path / "output.wav"
    return path


def voice_seed(voice_kind):
    if voice_kind is None or str(voice_kind).strip() == "":
        return None

    value = str(voice_kind).strip()
    try:
        return int(value)
    except ValueError:
        digest = hashlib.sha256(value.encode("utf-8")).digest()
        return int.from_bytes(digest[:4], "big")


def normalize_mixed_text(text):
    value = str(text).strip()
    value = value.replace("C++", "C plus plus").replace("c++", "C plus plus")
    value = value.replace("++", " plus plus ")
    value = re.sub(r"(?<=\w)\+(?=\w)", " plus ", value)
    value = value.replace("+", " plus ")
    value = value.replace("&", " and ")
    value = value.replace("@", " at ")
    value = value.replace("#", " sharp ")

    value = re.sub(r"(?<=[一-鿿])([A-Za-z0-9])", r" \1", value)
    value = re.sub(r"([A-Za-z0-9])(?=[一-鿿])", r"\1 ", value)

    for term, spoken in sorted(
        TECH_TERM_REPLACEMENTS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        value = re.sub(
            rf"(?<![A-Za-z0-9]){re.escape(term)}(?![A-Za-z0-9])",
            spoken,
            value,
        )

    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\s+([，。！？；：,.!?;:])", r"\1", value)
    return value.strip()


def split_text_for_tts(text):
    parts = []
    normalized_text = normalize_mixed_text(text)
    for sentence in re.split(r"(?<=[。！？!?；;])|\n+", normalized_text):
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) <= MAX_SEGMENT_CHARS:
            parts.append(sentence)
            continue

        current = ""
        for chunk in re.split(r"(?<=[，,、])", sentence):
            chunk = chunk.strip()
            if not chunk:
                continue
            if current and len(current) + len(chunk) > MAX_SEGMENT_CHARS:
                parts.append(current)
                current = chunk
            else:
                current += chunk
        if current:
            parts.append(current)

    return parts or [normalized_text]


def load_chat():
    chat = ChatTTS.Chat()
    load_models = getattr(chat, "load_models", None)
    if callable(load_models):
        load_models()
    else:
        chat.load(compile=False)
    return chat


def infer_wav(chat, voice_kind, text):
    seed = voice_seed(voice_kind)
    params_infer_code = None

    if seed is not None and hasattr(chat, "sample_random_speaker"):
        torch.manual_seed(seed)
        speaker = chat.sample_random_speaker()
        params_infer_code = ChatTTS.Chat.InferCodeParams(
            spk_emb=speaker,
            prompt="[speed_4]",
            temperature=0.25,
            repetition_penalty=1.1,
        )

    kwargs: dict[str, Any] = {
        "use_decoder": True,
        "skip_refine_text": True,
    }
    if params_infer_code is not None:
        kwargs["params_infer_code"] = params_infer_code

    segments = split_text_for_tts(text)
    wav_parts = []
    pause = np.zeros(int(SAMPLE_RATE * SENTENCE_PAUSE_SECONDS), dtype=np.float32)

    for index, segment in enumerate(segments):
        wavs = chat.infer([segment], split_text=False, **kwargs)
        wav_parts.append(to_mono_numpy(wavs[0]).astype(np.float32))
        if index < len(segments) - 1:
            wav_parts.append(pause)

    return np.concatenate(wav_parts)


def to_mono_numpy(wav):
    if isinstance(wav, torch.Tensor):
        wav = wav.detach().cpu().numpy()

    audio = np.asarray(wav)
    if audio.ndim > 1:
        audio = np.squeeze(audio)
    if audio.ndim != 1:
        raise ValueError(f"Expected mono audio, got shape {audio.shape}")
    return audio


def to_int16_pcm(wav):
    audio = to_mono_numpy(wav)

    if np.issubdtype(audio.dtype, np.floating):
        audio = np.clip(audio, -1.0, 1.0)
        audio = (audio * 32767.0).astype(np.int16)
    else:
        audio = audio.astype(np.int16)
    return audio


def write_wav(path, wav):
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = to_int16_pcm(wav)

    with wave.open(str(path), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(pcm.tobytes())


def main():
    parser = argparse.ArgumentParser(
        description="Generate a WAV file with ChatTTS.",
    )
    parser.add_argument(
        "voice_kind",
        help="Voice selector. Use a number or name for a deterministic voice.",
        default="2422",
    )
    parser.add_argument("text", help="Text to read.")
    parser.add_argument(
        "output_path",
        nargs="?",
        default=f"{os.getcwd()}/../voice_output.wav",
        help="Output .wav path or output directory. Empty value writes output.wav to ~/VoiceCloneResult.",
    )
    args = parser.parse_args()

    output_path = resolve_output_path(args.output_path)
    chat = load_chat()
    wav = infer_wav(chat, args.voice_kind, args.text)
    write_wav(output_path, wav)
    print(output_path)


if __name__ == "__main__":
    main()
