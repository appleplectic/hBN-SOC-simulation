# h-BN (V_B) Simulation
Determining the effects of spin-orbit coupling (SOC) on quantum emission simulations in monolayer hBN with a boron vacancy. 

## Usage
Pull and run the docker image `nvcr.io/nvidia/nvhpc:24.11-devel-cuda_multi-ubuntu22.04` or similar depending on your desired CUDA and Ubuntu versions.

Then, change the CUDA runtime version and `cc` version in `setup_espresso.sh` and run.

Finally, run `run.sh` to carry out the simulation. Note that you will need to copy over information from hbn_vb.atoms if you change `generate_structure.py`, and you may need to modify the `OCCUPATIONS` block in the excited-state calculations if the ground states change based on the output files with the `python3 generate_occupations.py <OUTFILE>` script.

Output files will be in the `out` directory.

## Pseudopotentials
Using pseudos from: https://dalcorso.github.io/pslibrary/, v1.0.0

Dal Corso, A. (2014). Pseudopotentials periodic table: From H to Pu. Computational Materials Science, 95, 337–350. doi:10.1016/j.commatsci.2014.07.043
