# How to relax PDBs for use with Rosetta software

1. uploaed all files into a single directory, along with PDBs to be relaxed
2. Run this script to submit all pdbs in the current directory for relaxation

  ```
  python3 submit_relax.py
  ```

starts a script that then runs relax_array.sbatch which submits individual jobs for each pdb

currently, it runs 10 jobs for each pdb with nstruct of 5 = 50 structures
* if it's a large protein, reduce the number of nstructs to 1 and increase jobs to 100

3. it will generate relaxed PDBs in relax_results folder
4. go into the relax_results folder and run this script

  ```
  python3 relax.py
  ```

it will automatically go into each folder and make a text file showing top 5 scored pdbs
will also print it in the terminal
