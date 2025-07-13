python generate_structure.py  # outputs hbn_vb.atoms; need to copy paste output

export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

screen -S qe-run bash -c "\ 
rm -rf scratch ; \ 
rm out/* ; \ 
mpirun -np 1 --bind-to none pw.x -in pw_scf_SOC.in > out/SOC.out ; \ 
mpirun -np 1 --bind-to none pw.x -in pw_scf_noSOC.in > out/noSOC.out ; \ 
cp -r ./scratch/hbn_vb_nosoc.save ./scratch/hbn_vb_excited_nosoc.save ; \ 
cp -r ./scratch/hbn_vb_soc.save ./scratch/hbn_vb_excited_soc.save ; \ 
mpirun -np 1 --bind-to none pw.x -in pw_scf_excited_noSOC.in > out/excited_noSOC.out ; \ 
mpirun -np 1 --bind-to none pw.x -in pw_scf_excited_SOC.in > out/excited_SOC.out ; \ 
"