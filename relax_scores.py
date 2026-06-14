#!/usr/bin/env python3

import os
import math
import shutil

TOP_N = 5
OUT_TXT_NAME = "top_5_scores.txt"
RESULTS_DIR = "relax_results"
TOP_DIR = "top_scores"


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


def write_txt(dest_dir, design_name, top_rows):
    out_path = os.path.join(dest_dir, OUT_TXT_NAME)
    with open(out_path, "w") as f:
        f.write(f"Top {TOP_N} rankings (lowest total_score/score) for: {design_name}\n")
        f.write(f"{'rank':<6}{'score':<15}description\n")
        f.write("-" * 80 + "\n")
        for i, (score, desc) in enumerate(top_rows, start=1):
            f.write(f"{i:<6}{score:<15.3f}{desc}\n")
    return out_path


def copy_top_pdbs(src_folder, dest_dir, top_rows):
    """
    Copy the PDB for each top decoy into dest_dir. The score file's
    'description' column is the decoy filename without the .pdb extension.
    Returns (copied, missing) filename lists.
    """
    copied = []
    missing = []
    for _, desc in top_rows:
        pdb_name = desc if desc.endswith(".pdb") else desc + ".pdb"
        src = os.path.join(src_folder, pdb_name)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(dest_dir, pdb_name))
            copied.append(pdb_name)
        else:
            missing.append(pdb_name)
    return copied, missing


def main():
    base = os.getcwd()
    results_path = os.path.join(base, RESULTS_DIR)

    if not os.path.isdir(results_path):
        print(f"No '{RESULTS_DIR}' folder found in: {base}")
        raise SystemExit(1)

    designs = sorted(
        d for d in os.listdir(results_path)
        if os.path.isdir(os.path.join(results_path, d)) and not d.startswith(".")
    )

    if not designs:
        print(f"No design subfolders found in '{RESULTS_DIR}'.")
        raise SystemExit(1)

    top_root = os.path.join(base, TOP_DIR)
    os.makedirs(top_root, exist_ok=True)

    processed = 0
    skipped = 0

    for design in designs:
        design_path = os.path.join(results_path, design)
        top_rows = top_scores_in_folder(design_path)

        if not top_rows:
            skipped += 1
            continue

        dest_dir = os.path.join(top_root, design)
        os.makedirs(dest_dir, exist_ok=True)

        out_path = write_txt(dest_dir, design, top_rows)
        copied, missing = copy_top_pdbs(design_path, dest_dir, top_rows)
        processed += 1

        # Print results too
        print(f"\n[{design}] Top {TOP_N}:")
        for i, (score, desc) in enumerate(top_rows, start=1):
            print(f"  {i}. {score:.3f}  {desc}")
        print(f"  -> wrote {out_path}")
        print(f"  -> copied {len(copied)} PDB(s) into {dest_dir}")
        if missing:
            print(f"  !! missing PDB(s): {', '.join(missing)}")

    print(f"\nDone. Processed: {processed} design(s). Skipped (no usable scores): {skipped} design(s).")
    print(f"Output folder: {top_root}")


if __name__ == "__main__":
    main()
