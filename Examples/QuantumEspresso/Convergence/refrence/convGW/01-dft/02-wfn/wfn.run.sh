#!/bin/bash


MPIRUN='srun -n 24 -c 2'
PW='pw.x'
PWFLAGS=''
PH='ph.x'
PHFLAGS=''

ln -nfs ../../01-density/GaAs.save/charge-density.dat GaAs.save/charge-density.dat
ln -nfs ../../01-density/GaAs.save/spin-polarization.dat GaAs.save/spin-polarization.dat

cp -f ../../../../../Data/Pseudos/31-Ga.PBE.UPF GaAs.save/31-Ga.PBE.UPF
cp -f ../../../../../Data/Pseudos/33-As.PBE.UPF GaAs.save/33-As.PBE.UPF
cp -f ../01-density/GaAs.save/data-file.xml GaAs.save/data-file.xml

$MPIRUN $PW $PWFLAGS -in wfn.in &> wfn.out

