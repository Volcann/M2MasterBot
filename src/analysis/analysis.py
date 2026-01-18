from __future__ import annotations

import argparse
import ast
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


@dataclass
class Config:
    input_path: str
    outdir: str
    top_n: int
    export_metrics: bool


def parse_matrix(s: str) -> Optional[np.ndarray]:
    if pd.isna(s):
        return None
    for loader in (ast.literal_eval, json.loads):
        try:
            parsed = loader(s)
        except Exception:
            continue
        try:
            arr = np.array(parsed, dtype=np.int64)
        except Exception:
            continue
        if arr.ndim == 2:
            return arr
    return None


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_clean(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"], low_memory=False)
    expected = {"timestamp", "score", "high_score", "highest_tile", "matrix"}
    if not expected.issubset(set(df.columns)):
        raise ValueError("Input CSV missing required columns")
    parsed: List[Optional[np.ndarray]] = []
    bad: List[int] = []
    for i, s in enumerate(df["matrix"]):
        mat = parse_matrix(s)
        if mat is None:
            bad.append(i)
            parsed.append(None)
        else:
            parsed.append(mat)
    df["matrix_parsed"] = parsed
    if bad:
        df = df.drop(index=bad).reset_index(drop=True)
    df["score"] = pd.to_numeric(df["score"], errors="coerce").astype("Int64")
    df["highest_tile"] = pd.to_numeric(df["highest_tile"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["timestamp", "score"]).reset_index(drop=True)
    return df


def plot_score_time_simple(df: pd.DataFrame, outpath: str) -> None:
    plt.rcParams.update({"font.size": 14, "figure.autolayout": True})
    df_sorted = df.sort_values("timestamp")
    timestamps = df_sorted["timestamp"]
    scores = df_sorted["score"].astype(int)
    plt.figure(figsize=(12, 5))
    plt.plot(timestamps, scores, marker="o", linewidth=1, markersize=6, alpha=0.8)
    window = max(3, int(min(len(scores), 20)))
    rolling = scores.rolling(window=window, min_periods=1).mean()
    plt.plot(timestamps, rolling, linewidth=2, linestyle="-", label="Trend")
    mean_val = float(np.mean(scores)) if len(scores) else 0.0
    med_val = float(np.median(scores)) if len(scores) else 0.0
    plt.axhline(mean_val, linestyle="--", linewidth=1.5, label=f"Mean {int(mean_val)}")
    plt.axhline(med_val, linestyle=":", linewidth=1.5, label=f"Median {int(med_val)}")
    if len(scores):
        last_ts = timestamps.iloc[-1]
        last_score = int(scores.iloc[-1])
        plt.annotate(f"Last: {last_score}", xy=(last_ts, last_score), xytext=(0, 10),
                     textcoords="offset points", ha="center")
    plt.title("Game score over time")
    plt.xlabel("Time")
    plt.ylabel("Score")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_score_distribution_simple(df: pd.DataFrame, outpath: str) -> None:
    plt.rcParams.update({"font.size": 14, "figure.autolayout": True})
    scores = df["score"].astype(int).values
    if len(scores) == 0:
        return
    bins = max(5, min(15, int(np.sqrt(len(scores)))))
    plt.figure(figsize=(10, 5))
    counts, edges, _ = plt.hist(scores, bins=bins, alpha=0.9)
    total = counts.sum()
    for i, c in enumerate(counts):
        pct = 100.0 * c / total if total else 0.0
        mid = (edges[i] + edges[i + 1]) / 2
        plt.text(mid, c + max(counts) * 0.02, f"{int(c)} ({pct:.0f}%)", ha="center")
    plt.title("Score ranges (how many games fall in each range)")
    plt.xlabel("Score")
    plt.ylabel("Number of games")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_tile_bar_simple(df: pd.DataFrame, outpath: str) -> None:
    plt.rcParams.update({"font.size": 14, "figure.autolayout": True})
    counts = df["highest_tile"].astype(int).value_counts()
    if counts.empty:
        return
    counts = counts.sort_values(ascending=True)
    labels = [str(x) for x in counts.index.tolist()]
    values = counts.values.tolist()
    plt.figure(figsize=(8, max(4, len(labels) * 0.5)))
    y_pos = range(len(labels))
    plt.barh(y_pos, values)
    plt.yticks(y_pos, labels)
    for i, v in enumerate(values):
        pct = 100.0 * v / sum(values) if sum(values) else 0.0
        plt.text(v + max(values) * 0.01, i, f"{v} ({pct:.0f}%)", va="center")
    plt.title("Most common highest tile")
    plt.xlabel("Count")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def smoothness_of_array(arr: np.ndarray) -> int:
    rows, cols = arr.shape
    smooth = 0
    for r in range(rows):
        for c in range(cols):
            v = int(arr[r, c])
            if c + 1 < cols:
                smooth += abs(v - int(arr[r, c + 1]))
            if r + 1 < rows:
                smooth += abs(v - int(arr[r + 1, c]))
    return int(smooth)


def potential_m2_merges(arr: np.ndarray) -> Tuple[int, int]:
    rows, cols = arr.shape
    centers = set()
    max_neighbors = 0
    for r in range(rows):
        for c in range(cols):
            val = int(arr[r, c])
            if val == 0:
                continue
            neighbors = 0
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and int(arr[nr, nc]) == val:
                    neighbors += 1
            if neighbors >= 2:
                centers.add((r, c))
            if neighbors > max_neighbors:
                max_neighbors = neighbors
    return len(centers), int(max_neighbors)


def analyze(cfg: Config) -> Dict[str, Any]:
    ensure_dir(cfg.outdir)
    df = load_clean(cfg.input_path)
    plot_score_time_simple(df, os.path.join(cfg.outdir, "score_over_time.png"))
    plot_score_distribution_simple(df, os.path.join(cfg.outdir, "score_distribution.png"))
    plot_tile_bar_simple(df, os.path.join(cfg.outdir, "highest_tile_simple.png"))
    outputs = {
        "score_over_time": os.path.join(cfg.outdir, "score_over_time.png"),
        "score_distribution": os.path.join(cfg.outdir, "score_distribution.png"),
        "highest_tile": os.path.join(cfg.outdir, "highest_tile_simple.png"),
    }
    if cfg.export_metrics:
        rows: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            mat = row["matrix_parsed"]
            arr = mat.astype(int)
            empty = int(np.sum(arr == 0))
            smooth = smoothness_of_array(arr)
            potential_merges, max_neighbors = potential_m2_merges(arr)
            highest_calc = int(arr.max()) if arr.size else 0
            rows.append({
                "timestamp": row["timestamp"],
                "score": int(row["score"]),
                "highest_tile_csv": int(row["highest_tile"]) if not pd.isna(row["highest_tile"]) else None,
                "highest_tile_calc": highest_calc,
                "empty_cells": empty,
                "smoothness": smooth,
                "potential_m2_merges": potential_merges,
                "max_neighbors_for_merge": max_neighbors,
                "matrix_shape": str(arr.shape),
            })
        out_csv = os.path.join(cfg.outdir, "derived_metrics_per_game.csv")
        pd.DataFrame(rows).to_csv(out_csv, index=False)
        outputs["derived_metrics_csv"] = out_csv
    return {"outputs": outputs}


def parse_args() -> Config:
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default="data/raw.csv")
    p.add_argument("--outdir", "-o", default="analysis_output")
    p.add_argument("--top", "-t", type=int, default=10)
    p.add_argument("--export-metrics", action="store_true")
    args = p.parse_args()
    return Config(input_path=args.input, outdir=args.outdir, top_n=args.top,
                  export_metrics=args.export_metrics)


if __name__ == "__main__":
    cfg = parse_args()
    analyze(cfg)
