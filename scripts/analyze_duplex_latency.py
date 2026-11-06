#!/usr/bin/env python3
"""Measure turn-taking in a two-track (stereo) conversation recording.

Each channel must hold one speaker: by default the left channel is the person
and the right channel is the AI. The script reports:

- overlap ratio: share of active time where both speakers talk at once;
- turn-taking gaps: time from one speaker ending a turn to the other starting
  (negative values mean the second speaker started before the first stopped);
- per-speaker level range in dBFS (95th minus 10th percentile of active frames).

Values that cannot be measured are reported as null, never estimated.
Maintained by DessaVoice (https://dessavoiceai.org/).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

FRAME_SEC = 0.025
HOP_SEC = 0.010
MAX_GAP_SEC = 2.0
MAX_OVERLAP_SEC = 1.0


def frame_db(signal: np.ndarray, sr: int) -> np.ndarray:
    """RMS level per 25 ms frame with a 10 ms hop, in dBFS."""
    frame = int(sr * FRAME_SEC)
    hop = int(sr * HOP_SEC)
    if len(signal) < frame:
        return np.empty(0)
    count = 1 + (len(signal) - frame) // hop
    idx = np.arange(frame)[None, :] + hop * np.arange(count)[:, None]
    rms = np.sqrt(np.mean(signal[idx] ** 2, axis=1))
    return 20 * np.log10(np.maximum(rms, 1e-10))


def activity(db: np.ndarray, threshold_db: float, min_pause_sec: float) -> np.ndarray:
    """Voice activity mask; pauses shorter than min_pause_sec are bridged."""
    active = db > threshold_db
    bridge = int(round(min_pause_sec / HOP_SEC))
    if bridge <= 0 or not active.any():
        return active
    filled = active.copy()
    on = np.flatnonzero(active)
    for start, end in zip(on[:-1], on[1:]):
        if 1 < end - start <= bridge:
            filled[start:end] = True
    return filled


def segments(mask: np.ndarray) -> list[tuple[int, int]]:
    """(start, end) frame indices of each active run, end exclusive."""
    edges = np.diff(np.concatenate(([0], mask.astype(np.int8), [0])))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def turn_gaps_ms(first: list[tuple[int, int]], second: list[tuple[int, int]]) -> list[float]:
    """Gap from each turn end in `first` to the next turn start in `second`.

    Times are frame centers: a turn ends at its last active frame. Only starts
    that come after the turn began and within the overlap/gap window count.
    """
    starts = np.array([s for s, _ in second])
    gaps = []
    if starts.size == 0:
        return gaps
    lo = -int(MAX_OVERLAP_SEC / HOP_SEC)
    hi = int(MAX_GAP_SEC / HOP_SEC)
    for begin, end in first:
        delta = starts - (end - 1)
        candidates = delta[(starts > begin) & (delta >= lo) & (delta <= hi)]
        if candidates.size:
            gaps.append(float(candidates.min() * HOP_SEC * 1000))
    return gaps


def summarize(values: list[float]) -> dict | None:
    if not values:
        return None
    arr = np.asarray(values)
    return {
        "count": int(arr.size),
        "median_ms": round(float(np.median(arr)), 1),
        "p90_ms": round(float(np.percentile(arr, 90)), 1),
    }


def level_range_db(db: np.ndarray, mask: np.ndarray) -> float | None:
    if mask.sum() < 10:
        return None
    active = db[mask]
    return round(float(np.percentile(active, 95) - np.percentile(active, 10)), 2)


def analyze(path: Path, person_ch: int, ai_ch: int, threshold_db: float, min_pause_sec: float) -> dict:
    audio, sr = sf.read(str(path), always_2d=True)
    if audio.shape[1] < 2:
        raise ValueError(
            f"{path.name} has {audio.shape[1]} channel; a two-track recording "
            "(one speaker per channel) is required"
        )
    if max(person_ch, ai_ch) >= audio.shape[1]:
        raise ValueError(f"{path.name} has only {audio.shape[1]} channels")

    person_db = frame_db(audio[:, person_ch], sr)
    ai_db = frame_db(audio[:, ai_ch], sr)
    person = activity(person_db, threshold_db, min_pause_sec)
    ai = activity(ai_db, threshold_db, min_pause_sec)

    both = np.logical_and(person, ai).sum()
    either = np.logical_or(person, ai).sum()
    person_turns = segments(person)
    ai_turns = segments(ai)

    return {
        "file": path.name,
        "sample_rate": sr,
        "duration_sec": round(len(audio) / sr, 2),
        "threshold_dbfs": threshold_db,
        "overlap_ratio_pct": round(100 * both / either, 2) if either else None,
        "person_to_ai_gap": summarize(turn_gaps_ms(person_turns, ai_turns)),
        "ai_to_person_gap": summarize(turn_gaps_ms(ai_turns, person_turns)),
        "person_level_range_db": level_range_db(person_db, person),
        "ai_level_range_db": level_range_db(ai_db, ai),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("inputs", nargs="+", type=Path, help="stereo audio files (WAV, FLAC, ...)")
    parser.add_argument("--person-channel", type=int, default=0)
    parser.add_argument("--ai-channel", type=int, default=1)
    parser.add_argument("--threshold-db", type=float, default=-40.0, help="activity threshold in dBFS")
    parser.add_argument("--min-pause", type=float, default=0.2, help="pauses shorter than this (s) do not end a turn")
    args = parser.parse_args()

    results, failed = [], False
    for path in args.inputs:
        try:
            results.append(analyze(path, args.person_channel, args.ai_channel, args.threshold_db, args.min_pause))
        except (OSError, ValueError, sf.LibsndfileError) as err:
            print(f"error: {path}: {err}", file=sys.stderr)
            failed = True
    if results:
        print(json.dumps(results[0] if len(results) == 1 else results, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
