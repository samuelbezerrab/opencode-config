#!/usr/bin/env python3
"""Local transcription and transcript-guided frames; no cloud writes."""
import argparse
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
MODEL = "mlx-community/whisper-large-v3-turbo"


def inspect_media(source):
    path = Path(source).expanduser().resolve(strict=True)
    if not path.is_file():
        raise ValueError("A mídia deve ser um arquivo local.")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type", "-of", "json", str(path)],
        check=True, capture_output=True, text=True, timeout=60,
    )
    data = json.loads(result.stdout)
    duration = float(data.get("format", {}).get("duration", 0))
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("Duração inválida ou desconhecida.")
    kinds = {stream.get("codec_type") for stream in data.get("streams", [])}
    with path.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    return path, duration, kinds, digest


def stamp(seconds):
    millis = round(seconds * 1000)
    hours, rest = divmod(millis, 3600000)
    minutes, rest = divmod(rest, 60000)
    seconds, millis = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"


def new_directory(path):
    output = Path(path).expanduser()
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    return output


def write_json(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, allow_nan=False)
        handle.write("\n")


def transcribe(args):
    source, duration, kinds, digest = inspect_media(args.source)
    if "audio" not in kinds:
        raise ValueError("O arquivo não contém áudio.")
    if Path(args.output_dir).expanduser().exists():
        raise FileExistsError("Use um novo diretório de saída; resultados anteriores são preservados.")
    import mlx_whisper

    start = time.monotonic()
    result = mlx_whisper.transcribe(
        str(source), path_or_hf_repo=MODEL,
        language=None if args.language == "auto" else args.language,
        task="transcribe", condition_on_previous_text=False, verbose=False,
    )
    rows = []
    for segment in result["segments"]:
        rows.append({
            "id": segment["id"], "start": segment["start"], "end": segment["end"],
            "text": segment["text"].strip(), "avg_logprob": segment["avg_logprob"],
            "no_speech_prob": segment["no_speech_prob"],
            "needs_review": segment["avg_logprob"] < -1 or segment["no_speech_prob"] > 0.6,
        })
    language = result["language"]
    data = {
        "source": source.name, "source_sha256": digest, "duration": duration,
        "has_video": "video" in kinds, "model": MODEL, "engine": "mlx-whisper",
        "language_requested": args.language, "language": language,
        "status": "transcribed" if rows else "no_speech_recognized",
        "elapsed_seconds": round(time.monotonic() - start, 2),
        "peak_rss_mib": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024 * 1024 if sys.platform == "darwin" else 1024), 1),
        "segments": rows,
    }
    output = new_directory(args.output_dir)
    write_json(output / "transcript.json", data)
    (output / "transcript.txt").write_text(
        "\n".join(row["text"] for row in rows) + "\n", encoding="utf-8")
    lines = ["# Transcrição", "", f"Idioma: {language}; modelo: turbo; motor: MLX Whisper.",
             "", "Transcrição automática: revisar trechos incertos antes de agir.", ""]
    if not rows:
        lines.append("Nenhuma fala reconhecida; não inferir demandas a partir deste resultado.")
    for row in rows:
        note = " [revisar]" if row["needs_review"] else ""
        lines.append(f"- [{stamp(row['start'])}–{stamp(row['end'])}] "
                     f"(segmento {row['id']}){note} {row['text']}")
    (output / "transcript.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output_dir": str(output), "segments": len(rows),
                      "status": data["status"], "elapsed_seconds": data["elapsed_seconds"],
                      "peak_rss_mib": data["peak_rss_mib"]}, ensure_ascii=False))


def validate_selection(selection, transcript, duration, digest):
    if transcript.get("source_sha256") != digest:
        raise ValueError("A transcrição não corresponde ao arquivo original.")
    if not isinstance(selection, list) or not 1 <= len(selection) <= 8:
        raise ValueError("Selecione de 1 a 8 frames após analisar a transcrição.")
    segments = {row["id"]: row for row in transcript["segments"]}
    for item in selection:
        timestamp = float(item["timestamp"])
        if not math.isfinite(timestamp) or not 0 <= timestamp < duration:
            raise ValueError("Timestamp fora da duração do vídeo.")
        if item["segment_id"] not in segments:
            raise ValueError("segment_id não existe na transcrição.")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise ValueError("Cada frame precisa de uma justificativa baseada na transcrição.")
    return segments


def frames(args):
    source, duration, kinds, digest = inspect_media(args.source)
    if "video" not in kinds:
        raise ValueError("Extração de frames requer uma mídia com vídeo.")
    transcript = json.loads(Path(args.transcript).read_text(encoding="utf-8"))
    selection = json.loads(Path(args.selection).read_text(encoding="utf-8"))
    segments = validate_selection(selection, transcript, duration, digest)
    output = new_directory(args.output_dir)
    lines = ["# Frames selecionados após análise da transcrição", "",
             "Inspecione as imagens antes de tratá-las como evidência validada.", ""]
    for index, item in enumerate(selection, 1):
        timestamp = float(item["timestamp"])
        label = re.sub(r"[^a-z0-9]+", "-", str(item.get("label", "frame")).lower()).strip("-")[:60]
        image = output / f"frame-{index:02}-{label or 'frame'}.png"
        subprocess.run([
            "ffmpeg", "-nostdin", "-n", "-hide_banner", "-loglevel", "error",
            "-threads", "2", "-ss", str(timestamp), "-i", str(source),
            "-map", "0:v:0", "-frames:v", "1", "-vf", "scale='min(1280,iw)':-2",
            "-threads", "2", str(image),
        ], check=True, timeout=120)
        if not image.is_file() or image.stat().st_size == 0:
            raise ValueError(f"Não foi gerado frame no instante {timestamp}.")
        row = segments[item["segment_id"]]
        lines.extend([f"## {stamp(timestamp)} — {image.name}", "",
                      f"Motivo: {item['reason']}",
                      f"Fala [{stamp(row['start'])}–{stamp(row['end'])}]: {row['text']}",
                      "", f"![Frame em {stamp(timestamp)}]({image.name})", ""])
    (output / "screenshots.md").write_text("\n".join(lines), encoding="utf-8")
    write_json(output / "selection.json", selection)
    print(json.dumps({"output_dir": str(output), "frames": len(selection)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    audio = commands.add_parser("transcribe", help="Transcrever localmente com MLX Whisper turbo")
    audio.add_argument("source")
    audio.add_argument("--output-dir", required=True)
    audio.add_argument("--language", default="pt")
    visual = commands.add_parser("frames", help="Extrair frames escolhidos após análise da fala")
    visual.add_argument("source")
    visual.add_argument("--transcript", required=True)
    visual.add_argument("--selection", required=True)
    visual.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    os.umask(0o077)
    state = Path.home() / ".local/state/transcribe-media"
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    with (state / "execution.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("Transcrição/extração ocupada. Tente novamente mais tarde.", file=sys.stderr)
            return 75
        try:
            (transcribe if args.command == "transcribe" else frames)(args)
        except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
            print(f"Falha: {error}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
