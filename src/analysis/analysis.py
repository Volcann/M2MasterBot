from __future__ import annotations

import argparse
import ast
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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
    try:
        parsed = ast.literal_eval(s)
        arr = np.array(parsed, dtype=np.int64)
        if arr.shape == (4, 4):
            return arr
    except Exception:
        try:
            parsed = json.loads(s)
            arr = np.array(parsed, dtype=np.int64)
            if arr.shape == (4, 4):
                return arr
        except Exception:
            return None
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
    df["high_score"] = pd.to_numeric(df["high_score"], errors="coerce").astype("Int64")
    df["highest_tile"] = (
        pd.to_numeric(df["highest_tile"], errors="coerce").astype("Int64")
    )
    df = df.dropna(subset=["timestamp", "score"]).reset_index(drop=True)
    return df


def core_perf(df: pd.DataFrame, top_n: int = 10) -> Dict[str, Any]:
    total = len(df)
    scores = df["score"].astype(int).values
    avg = float(np.nanmean(scores)) if total else 0.0
    med = float(np.nanmedian(scores)) if total else 0.0
    mx = int(np.nanmax(scores)) if total else 0
    std = float(np.nanstd(scores)) if total else 0.0
    hist_vals, hist_edges = np.histogram(scores, bins="auto")
    df_sorted = df.sort_values("timestamp").reset_index(drop=True)
    running_highs = df_sorted["high_score"].astype(int).values.tolist()
    tile_counts = df["highest_tile"].value_counts().sort_index().to_dict()
    top = df.nlargest(top_n, "score")[["timestamp", "score", "highest_tile"]]
    bot = df.nsmallest(top_n, "score")[["timestamp", "score", "highest_tile"]]
    return {
        "total_games": total,
        "average_score": avg,
        "median_score": med,
        "max_score": mx,
        "score_std": std,
        "score_hist": (hist_vals.tolist(), hist_edges.tolist()),
        "running_highs": running_highs,
        "highest_tile_counts": {int(k): int(v) for k, v in tile_counts.items()},
        "top_games": top.to_dict(orient="records"),
        "bottom_games": bot.to_dict(orient="records"),
    }


def board_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    matrices = df["matrix_parsed"].tolist()
    mats = np.stack(matrices, axis=0).astype(np.int64)
    avg_tile = np.mean(mats, axis=0)
    unique, counts = np.unique(mats, return_counts=True)
    tile_freq = dict(zip(map(int, unique.tolist()), counts.tolist()))
    corners = [(0, 0), (0, 3), (3, 0), (3, 3)]
    corner_dom = 0
    corner_counts = {c: 0 for c in corners}
    total = mats.shape[0]
    for i in range(total):
        mat = mats[i]
        mv = int(mat.max())
        positions = list(zip(*np.where(mat == mv)))
        any_corner = any(pos in corners for pos in positions)
        if any_corner:
            corner_dom += 1
            for c in corners:
                if c in positions:
                    corner_counts[c] += 1
    corner_pct = 100.0 * corner_dom / total if total else 0.0
    smooth_scores: List[int] = []
    for mat in mats:
        s = 0
        for r in range(4):
            for c in range(4):
                v = mat[r, c]
                if c < 3:
                    s += abs(int(v) - int(mat[r, c + 1]))
                if r < 3:
                    s += abs(int(v) - int(mat[r + 1, c]))
        smooth_scores.append(s)
    smooth_arr = np.array(smooth_scores)
    def mono_score(mat: np.ndarray) -> float:
        score = 0.0
        for r in range(4):
            row = mat[r, :].astype(np.float64)
            desc_diff = np.sum(np.abs(np.diff(row) < 0))
            score += desc_diff
        for c in range(4):
            col = mat[:, c].astype(np.float64)
            desc_diff = np.sum(np.abs(np.diff(col) < 0))
            score += desc_diff
        return float(score)
    mono_scores = np.array([mono_score(mat) for mat in mats])
    empty_counts = np.sum(mats == 0, axis=(1, 2))
    scores = df["score"].astype(int).values
    try:
        corr = float(np.corrcoef(empty_counts, scores)[0, 1])
    except Exception:
        corr = float("nan")
    return {
        "avg_tile_matrix": avg_tile.tolist(),
        "tile_frequency": tile_freq,
        "corner_dominance_pct": corner_pct,
        "corner_counts": {str(k): int(v) for k, v in corner_counts.items()},
        "smoothness_mean": float(np.mean(smooth_arr)),
        "smoothness_median": float(np.median(smooth_arr)),
        "monotonicity_mean": float(np.mean(mono_scores)),
        "empty_cell_stats": {
            "mean": float(np.mean(empty_counts)),
            "median": float(np.median(empty_counts)),
        },
        "empty_vs_score_corr": corr,
    }


def time_insights(df: pd.DataFrame) -> Dict[str, Any]:
    df_t = df.sort_values("timestamp").reset_index(drop=True)
    df_t["score_int"] = df_t["score"].astype(int)
    window = max(3, int(min(len(df_t), 20)))
    df_t["rolling_mean"] = df_t["score_int"].rolling(window=window, min_periods=1).mean()
    df_t["rolling_std"] = (
        df_t["score_int"].rolling(window=window, min_periods=1).std().fillna(0)
    )
    scores = df_t["score_int"].values
    inc_streaks: List[int] = []
    dec_streaks: List[int] = []
    current_inc = 1
    current_dec = 1
    for i in range(1, len(scores)):
        if scores[i] > scores[i - 1]:
            current_inc += 1
            inc_streaks.append(current_inc)
            current_dec = 1
        elif scores[i] < scores[i - 1]:
            current_dec += 1
            dec_streaks.append(current_dec)
            current_inc = 1
        else:
            current_inc = 1
            current_dec = 1
    best_inc = max(inc_streaks) if inc_streaks else 1
    best_dec = max(dec_streaks) if dec_streaks else 1
    return {
        "rolling_window": window,
        "rolling_mean_series": df_t["rolling_mean"].tolist(),
        "rolling_std_series": df_t["rolling_std"].tolist(),
        "best_increasing_streak": int(best_inc),
        "best_decreasing_streak": int(best_dec),
    }


def plot_score_time(df: pd.DataFrame, outpath: str) -> None:
    plt.figure(figsize=(10, 4))
    df_sorted = df.sort_values("timestamp")
    plt.plot(df_sorted["timestamp"], df_sorted["score"].astype(int), marker=".", linewidth=1)
    plt.title("Score over Time")
    plt.xlabel("Time")
    plt.ylabel("Score")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_tile_freq(tile_freq: Dict[int, int], outpath: str) -> None:
    items = sorted(tile_freq.items())
    tiles = [str(k) for k, _ in items]
    counts = [v for _, v in items]
    plt.figure(figsize=(8, 4))
    plt.bar(tiles, counts)
    plt.title("Highest Tile Frequency")
    plt.xlabel("Tile")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_heatmap(avg_matrix: List[List[float]], outpath: str) -> None:
    arr = np.array(avg_matrix)
    plt.figure(figsize=(4, 4))
    plt.imshow(arr, interpolation="nearest")
    plt.title("Average Tile Value per Position")
    plt.colorbar()
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def plot_hist(df: pd.DataFrame, outpath: str) -> None:
    scores = df["score"].astype(int).values
    plt.figure(figsize=(8, 4))
    plt.hist(scores, bins="auto")
    plt.title("Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()


def console_report(core: Dict[str, Any], board: Dict[str, Any], timei: Dict[str, Any]) -> None:
    print("\n===== 2048 Bot Analysis Summary =====\n")
    print(f"Total games: {core['total_games']}")
    print(f"Average score: {core['average_score']:.2f}")
    print(f"Median score: {core['median_score']:.2f}")
    print(f"Max score: {core['max_score']}")
    print(f"Score stddev: {core['score_std']:.2f}")
    print(f"Corner dominance: {board['corner_dominance_pct']:.2f}%")
    print(f"Avg smoothness: {board['smoothness_mean']:.2f}")
    print(f"Empty cells mean: {board['empty_cell_stats']['mean']:.2f}")
    print(f"Empty-vs-score correlation: {board['empty_vs_score_corr']:.3f}")
    print(f"Best increasing streak: {timei['best_increasing_streak']}")
    print(f"Best decreasing streak: {timei['best_decreasing_streak']}\n")
    print("Top games sample:")
    for g in core["top_games"]:
        ts = pd.to_datetime(g["timestamp"]) if g.get("timestamp") is not None else ""
        print(f" - {ts} | score={g['score']} | highest_tile={g['highest_tile']}")
    print("\n")


def export_metrics(df: pd.DataFrame, outdir: str) -> str:
    rows: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        mat = row["matrix_parsed"]
        arr = mat.astype(int)
        empty = int(np.sum(arr == 0))
        smooth = 0
        for r in range(4):
            for c in range(4):
                if c < 3:
                    smooth += abs(int(arr[r, c]) - int(arr[r, c + 1]))
                if r < 3:
                    smooth += abs(int(arr[r, c]) - int(arr[r + 1, c]))
        rows.append({
            "timestamp": row["timestamp"],
            "score": int(row["score"]),
            "highest_tile": int(row["highest_tile"]),
            "empty_cells": empty,
            "smoothness": smooth,
        })
    out_csv = os.path.join(outdir, "derived_metrics_per_game.csv")
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    return out_csv


def analyze(cfg: Config) -> Dict[str, Any]:
    ensure_dir(cfg.outdir)
    df = load_clean(cfg.input_path)
    core = core_perf(df, top_n=cfg.top_n)
    board = board_analysis(df)
    timei = time_insights(df)
    plot_score_time(df, os.path.join(cfg.outdir, "score_over_time.png"))
    plot_tile_freq(core["highest_tile_counts"], os.path.join(cfg.outdir, "highest_tile_freq.png"))
    plot_heatmap(board["avg_tile_matrix"], os.path.join(cfg.outdir, "avg_tile_heatmap.png"))
    plot_hist(df, os.path.join(cfg.outdir, "score_histogram.png"))
    console_report(core, board, timei)
    result = {
        "core": core,
        "board": board,
        "time": timei,
        "outputs": {
            "score_over_time": os.path.join(cfg.outdir, "score_over_time.png"),
            "highest_tile_freq": os.path.join(cfg.outdir, "highest_tile_freq.png"),
            "avg_tile_heatmap": os.path.join(cfg.outdir, "avg_tile_heatmap.png"),
            "score_histogram": os.path.join(cfg.outdir, "score_histogram.png"),
        },
    }
    if cfg.export_metrics:
        csv_path = export_metrics(df, cfg.outdir)
        result["outputs"]["derived_metrics_csv"] = csv_path
        print(f"Exported derived metrics to: {csv_path}")
    print(f"Saved charts to: {cfg.outdir}")
    return result


def parse_args() -> Config:
    p = argparse.ArgumentParser()
    p.add_argument("--input", "-i", default="data/raw.csv")
    p.add_argument("--outdir", "-o", default="analysis_out")
    p.add_argument("--top", "-t", type=int, default=10)
    p.add_argument("--export-metrics", action="store_true")
    args = p.parse_args()
    return Config(input_path=args.input, outdir=args.outdir, top_n=args.top, export_metrics=args.export_metrics)


if __name__ == "__main__":
    cfg = parse_args()
    analyze(cfg)
