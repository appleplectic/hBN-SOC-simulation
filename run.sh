python generate_structure.py          # outputs hbn_vb.atoms; need to copy paste output

export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

mpirun -np 1 --bind-to none pw.x -in pw_scf_SOC.in > out/SOC.out
mpirun -np 1 --bind-to none pw.x -in pw_scf_noSOC.in > out/noSOC.out
mpirun -np 1 --bind-to none pw.x -in pw_scf_excited_noSOC.in > out/excited_noSOC.out
mpirun -np 1 --bind-to none pw.x -in pw_scf_excited_SOC.in > out/excited_SOC.out
