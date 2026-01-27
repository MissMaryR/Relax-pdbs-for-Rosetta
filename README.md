# Submits all pdbs in the current directory for relaxation

   run with 

  ```
  python3 submit_relax.py
  ```

starts a script that then runs relax_array.sbatch 

which submits individual jobs for each pdb

currently, runs 10 jobs for each pdb with nstruct of 5 = 50 structures

#makes a relax_results folder with pdbs
have relax_score.py in the relax_results folder and run with 
  ```
  python3 relax_score.py
  ```
will go into each folder and make a text file showing top 5 scored pdbs
also will print it in the terminal
