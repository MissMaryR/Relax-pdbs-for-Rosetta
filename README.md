# relax_faster

Scripts for running Rosetta FastRelax at scale on the Siegel Lab HIVE cluster (SLURM). Submits one array job per input PDB, then collects the top-scoring structures when the jobs finish.

## Workflow

### 1. Submit relaxation jobs

Place all input PDB files in the current directory, then run:

```bash
python submit_relax.py
```

This finds every `*.pdb` in the working directory and submits a 40-task SLURM array job for each one via `relax_array.sbatch`. Each task produces one relaxed structure (`-nstruct 1`), giving 40 independent relaxed models per input. Output PDBs and score files land in `relax_results/<basename>/`.

### 2. Collect top scores

After all jobs complete:

```bash
python relax_scores.py
```

Run this in the same directory as the `relax_results/` folder. For each subfolder it:

- Parses all `score*.sc` files
- Selects the 5 lowest-scoring (best) structures
- Writes a ranked summary to `top_5_scores.txt`
- Copies the 5 best PDBs into separate folders for each submission into a `top_scores/` folder

## Files

| File | Purpose |
|------|---------|
| `submit_relax.py` | Submits one SLURM array job per PDB in the current directory |
| `relax_array.sbatch` | SLURM array script (40 tasks, 1 struct/task); takes a PDB path as argument |
| `relax_scores.py` | Parses score files, ranks structures, collects best PDBs |
| `fast_relax.sh` | Simple single-job script for faster runs |

## Rosetta flags used

| Flag | Effect |
|------|--------|
| `-ex1 -ex2` | Extra rotamer sampling for chi1/chi2 |
| `-use_input_sc` | Include input side-chain rotamers |
| `-flip_HNQ` | Sample His/Asn/Gln flips |
| `-relax:constrain_relax_to_start_coords` | Backbone constrained to input coordinates |
| `-relax:coord_constrain_sidechains` | Side-chain heavy atoms also constrained |
| `-relax:ramp_constraints false` | Constraints held constant (not ramped) |
| `-default_max_cycles 200` | Limits minimization cycles for speed - only in fast_relax |

## Requirements

- Access to the Siegel Lab HIVE cluster
- Rosetta 3.14 at `/quobyte/jbsiegelgrp/software/Rosetta_314/`
- Python 3 (standard library only)
