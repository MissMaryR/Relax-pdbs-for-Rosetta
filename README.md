# Submits all pdbs in the current directory for relaxation

   run with 

  ```
  python3 submit_relax.py
  ```

starts a script that then runs relax_array.sbatch 

which submits individual jobs for each pdb

currently, runs 10 jobs for each pdb with nstruct of 5 = 50 structures
