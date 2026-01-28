#!/usr/bin/env python3

import os
import math

TOP_N = 5
OUT_TXT_NAME = "top_5_scores.txt"


def safe_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return float("nan")


def parse_rosetta_sc(sc_path):
    """
    Parse a Rosetta scorefile (.sc) and return a list of (score, description) tuples.
    Prefers column 'total_score'; falls back to 'score' if needed.
    """
    header = None
    score_idx = None
    desc_idx = None
    rows = []

    with open(sc_path, "r") as f:
        for line in f:
            if not line.startswith("SCORE:"):
                continue

            tokens = line.strip().split()
            if len(tokens) < 3:
                continue

            # Remove the leading "SCORE:"
            fields = tokens[1:]

            # Detect header line (contains 'description' and a score column name)
            if ("description" in fields) and (("total_score" in fields) or ("score" in fields)):
                header = fields
                score_idx = header.index("total_score") if "total_score" in header else header.index("score")
                desc_idx = header.index("description") if "description" in header else (len(header) - 1)
                continue

            # If we haven't found a header yet, we can't reliably parse data rows
            if header is None or score_idx is None:
                continue

            # Some scorefiles repeat the header; skip if it matches
            if fields and fields[0] == header[0]:
                continue

            if len(fields) < len(header):
                continue

            score = safe_float(fields[score_idx])
            if math.isnan(score):
                continue

            desc = fields[desc_idx] if desc_idx < len(fields) else fields[-1]
            rows.append((score, desc))

    return rows


def top_scores_in_folder(folder_path):
    all_rows = []

    for fname in os.listdir(folder_path):
        if fname.startswith("score") and fname.endswith(".sc"):
            sc_path = os.path.join(folder_path, fname)
            try:
                all_rows.extend(parse_rosetta_sc(sc_path))
            except Exception as e:
                print(f"[{os.path.basename(folder_path)}] Error reading {fname}: {e}")

    if not all_rows:
        return []

    all_rows.sort(key=lambda x: x[0])  # lowest score first
    return all_rows[:TOP_N]


def write_txt(folder_path, top_rows):
    out_path = os.path.join(folder_path, OUT_TXT_NAME)
    with open(out_path, "w") as f:
        f.write(f"Top {TOP_N} rankings (lowest total_score/score) for: {os.path.basename(folder_path)}\n")
        f.write(f"{'rank':<6}{'score':<15}description\n")
        f.write("-" * 80 + "\n")
        for i, (score, desc) in enumerate(top_rows, start=1):
            f.write(f"{i:<6}{score:<15.3f}{desc}\n")
    return out_path


def main():
    base = os.getcwd()

    subfolders = sorted(
        d for d in os.listdir(base)
        if os.path.isdir(os.path.join(base, d)) and not d.startswith(".")
    )

    if not subfolders:
        print("No subfolders found in the current directory.")
        raise SystemExit(1)

    processed = 0
    skipped = 0

    for folder in subfolders:
        folder_path = os.path.join(base, folder)
        top_rows = top_scores_in_folder(folder_path)

        if not top_rows:
            skipped += 1
            continue

        out_path = write_txt(folder_path, top_rows)
        processed += 1

        # Print results too
        print(f"\n[{folder}] Top {TOP_N}:")
        for i, (score, desc) in enumerate(top_rows, start=1):
            print(f"  {i}. {score:.3f}  {desc}")
        print(f"  -> wrote {out_path}")

    print(f"\nDone. Processed: {processed} folders. Skipped (no usable scores): {skipped} folders.")


if __name__ == "__main__":
    main()
