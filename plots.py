#!/usr/bin/env python3
"""
Plot all training/eval figures for the RL Pokémon project.

Usage:
  python analysis/plot_all.py --logs logs --db optuna_studies.db --out docs --ma 100
"""

import argparse
import math
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# ---------- helpers ----------
def ensure_dirs(outdir: Path):
    (outdir / "figs").mkdir(parents=True, exist_ok=True)
    (outdir / "tables").mkdir(parents=True, exist_ok=True)

def moving_average(x, w):
    if w <= 1:
        return x
    return x.rolling(window=w, min_periods=1, center=False).mean()

def simple_line(df, x, y, title, outpath, ma=None):
    plt.figure()
    if ma and y in df.columns:
        plt.plot(df[x], moving_average(df[y], ma), label=f"{y} (MA{ma})")
        plt.plot(df[x], df[y], alpha=0.25, label=y)
        plt.legend()
    else:
        plt.plot(df[x], df[y])
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig(outpath)
    plt.close()

def save_preview_table(df: pd.DataFrame, out_csv: Path, n=10):
    df.head(n).to_csv(out_csv, index=False)

# ---------- per-run figures ----------
def plot_run(csv_path: Path, outdir: Path, ma_win: int):
    run_name = csv_path.stem
    df = pd.read_csv(csv_path)
    # normalize expected columns
    # typical columns: episode, train_return, steps|episode_length, epsilon, q_rows, eval_winrate, eval_return
    if "episode" not in df.columns:
        raise ValueError(f"{csv_path} has no 'episode' column.")
    # map alternative names
    if "steps" in df.columns and "episode_length" not in df.columns:
        df["episode_length"] = df["steps"]

    figs = outdir / "figs"
    # Train return
    if "train_return" in df.columns:
        simple_line(df, "episode", "train_return",
                    f"{run_name}: Train return per episode",
                    figs / f"{run_name}_train_return.png",
                    ma=ma_win)
    # Episode length
    if "episode_length" in df.columns:
        simple_line(df, "episode", "episode_length",
                    f"{run_name}: Episode length",
                    figs / f"{run_name}_episode_length.png",
                    ma=ma_win)
    # Epsilon
    if "epsilon" in df.columns:
        simple_line(df, "episode", "epsilon",
                    f"{run_name}: Epsilon schedule",
                    figs / f"{run_name}_epsilon.png")
    # Greedy eval win-rate
    if "eval_winrate" in df.columns and df["eval_winrate"].notna().any():
        simple_line(df[df["eval_winrate"].notna()], "episode", "eval_winrate",
                    f"{run_name}: Greedy eval win-rate",
                    figs / f"{run_name}_eval_winrate.png")
    # Q rows (visited states proxy)
    if "q_rows" in df.columns and df["q_rows"].notna().any():
        simple_line(df, "episode", "q_rows",
                    f"{run_name}: Unique Q rows (state coverage proxy)",
                    figs / f"{run_name}_q_rows.png")

    # Save a tiny summary for the appendix
    last = df.tail(1).to_dict(orient="records")[0]
    summary = {
        "run": run_name,
        "episodes": int(df["episode"].max()),
        "final_train_return": float(last.get("train_return")) if "train_return" in df.columns else None,
        "final_episode_length": float(last.get("episode_length")) if "episode_length" in df.columns else None,
        "final_epsilon": float(last.get("epsilon")) if "epsilon" in df.columns else None,
        "final_eval_winrate": float(last.get("eval_winrate")) if "eval_winrate" in df.columns and not math.isnan(last.get("eval_winrate", float("nan"))) else None,
        "final_eval_return": float(last.get("eval_return")) if "eval_return" in df.columns and not math.isnan(last.get("eval_return", float("nan"))) else None,
        "max_q_rows": int(df["q_rows"].max()) if "q_rows" in df.columns else None,
    }
    return summary

# ---------- optuna ----------
def analyze_optuna(db_path: Path, outdir: Path, study_like: str = ""):
    if not db_path.exists():
        return None
    con = sqlite3.connect(db_path)
    try:
        studies = pd.read_sql_query("SELECT study_id, study_name FROM studies;", con)
        trials = pd.read_sql_query(
            """
            SELECT s.study_name, t.trial_id, t.number AS trial_number, t.state,
                   tv.value, tp.param_name, tp.param_value
            FROM trials t
            LEFT JOIN trial_values tv ON t.trial_id = tv.trial_id
            LEFT JOIN trial_params tp ON t.trial_id = tp.trial_id
            LEFT JOIN studies s ON s.study_id = t.study_id
            """,
            con,
        )
    finally:
        con.close()
    if trials.empty:
        return None

    if study_like:
        trials = trials[trials["study_name"].str.contains(study_like, case=False, na=False)]

    # pivot params for readability
    piv = trials.pivot_table(index=["study_name","trial_number","state","value"],
                             columns="param_name", values="param_value", aggfunc="first").reset_index()
    piv.to_csv(outdir / "tables" / "optuna_trials_flat.csv", index=False)

    # top-10 by value per study
    best = piv.sort_values(["study_name","value"], ascending=[True, False]).groupby("study_name").head(10)
    best.to_csv(outdir / "tables" / "optuna_top10.csv", index=False)

    # bar plot of top values by study (first 10 rows)
    for study in best["study_name"].unique():
        sub = best[best["study_name"] == study]
        plt.figure()
        plt.bar(sub["trial_number"].astype(str), sub["value"])
        plt.title(f"Optuna top trials — {study}")
        plt.xlabel("trial_number")
        plt.ylabel("objective value")
        plt.tight_layout()
        plt.savefig(outdir / "figs" / f"optuna_top_{study.replace(' ','_')}.png")
        plt.close()

    return {"studies": studies, "best": best}

# ---------- main ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--logs", type=str, default="./logs", help="logs directory")
    ap.add_argument("--db", type=str, default="optuna_studies.db", help="Optuna SQLite path")
    ap.add_argument("--out", type=str, default="./plots", help="output directory")
    ap.add_argument("--ma", type=int, default=100, help="moving average window (episodes)")
    ap.add_argument("--study_like", type=str, default="", help="filter study names containing this string")
    args = ap.parse_args()

    logs_dir = Path(args.logs)
    outdir = Path(args.out)
    ensure_dirs(outdir)

    # Plot each run
    summaries = []
    for csv in sorted(logs_dir.glob("*.csv")):
        try:
            summaries.append(plot_run(csv, outdir, args.ma))
        except Exception as e:
            print(f"[WARN] Skipping {csv.name}: {e}")

    if summaries:
        pd.DataFrame(summaries).to_csv(outdir / "tables" / "training_summaries.csv", index=False)

    # Optuna
    analyze_optuna(Path(args.db), outdir, study_like=args.study_like)

    print(f"Done. Figures -> {outdir/'figs'}, Tables -> {outdir/'tables'}")

if __name__ == "__main__":
    main()
