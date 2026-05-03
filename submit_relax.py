#!/usr/bin/env python3
import glob
import os
import re
import subprocess
import sys

SBATCH_SCRIPT = "relax_array.sbatch"

def submit_one(pdb_path: str) -> str:
    base = os.path.splitext(os.path.basename(pdb_path))[0]
    os.makedirs("logs", exist_ok=True)

    cmd = [
        "sbatch",
        f"--job-name=relax_{base}",
        f"--output=logs/relax_{base}_%A_%a.out",
        f"--error=logs/relax_{base}_%A_%a.err",
        SBATCH_SCRIPT,
        pdb_path,
    ]

    res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out = (res.stdout or "").strip()

    m = re.search(r"Submitted batch job (\d+)", out)
    jobid = m.group(1) if m else "UNKNOWN"
    return jobid

def main():
    if not os.path.isfile(SBATCH_SCRIPT):
        print(f"ERROR: Can't find sbatch script: {SBATCH_SCRIPT}", file=sys.stderr)
        print("Put relax_array.sbatch in this directory (or edit SBATCH_SCRIPT in the python file).", file=sys.stderr)
        sys.exit(1)

    pdbs = sorted(glob.glob("*.pdb"))
    if not pdbs:
        print("ERROR: No *.pdb files found in the current directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(pdbs)} PDB(s). Submitting one SLURM array job per PDB...")
    for pdb in pdbs:
        jobid = submit_one(pdb)
        print(f"  {pdb} -> job {jobid}")

if __name__ == "__main__":
    main()
