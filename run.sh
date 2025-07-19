echo "Generating hbn_vb.atoms..."
python generate_structure.py

echo "Generated; copy output into *.in files. Press enter to continue..."
read

export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

mkdir out
rm -rf scratch
rm out/*

echo "Running ground state no SOC calculations..."
mpirun -np 1 --bind-to none pw.x -in pw_scf_noSOC.in > out/noSOC.out
mpirun -np 1 --bind-to none pw.x -in pw_nscf_noSOC.in > out/nscf_noSOC.out

echo "Running ground state SOC calculations..."
cp -r scratch/hbn_vb_nosoc.save scratch/hbn_vb_soc.save
mpirun -np 1 --bind-to none pw.x -in pw_scf_SOC.in > out/SOC.out
mpirun -np 1 --bind-to none pw.x -in pw_nscf_SOC.in > out/nscf_SOC.out

echo "Generating OCCUPATIONS blocks (occ_noSOC.out & occ_SOC.out)..."
python3 generate_occupations.py out/noSOC.out 150 > occ_noSOC.out
python3 generate_occupations.py out/SOC.out 300 > occ_SOC.out
echo "Generated; copy output into *.in files. Press enter to continue..."
read

echo "Running excited state no SOC calculations..."
cp -r scratch/hbn_vb_nosoc.save scratch/hbn_vb_excited_nosoc.save
mpirun -np 1 --bind-to none pw.x -in pw_scf_excited_noSOC.in > out/excited_noSOC.out 
mpirun -np 1 --bind-to none pw.x -in pw_nscf_excited_noSOC.in > out/nscf_excited_noSOC.out

echo "Running excited state SOC calculations..."
cp -r scratch/hbn_vb_soc.save scratch/hbn_vb_excited_soc.save
mpirun -np 1 --bind-to none pw.x -in pw_scf_excited_SOC.in > out/excited_SOC.out 
mpirun -np 1 --bind-to none pw.x -in pw_nscf_excited_SOC.in > out/nscf_excited_SOC.out
