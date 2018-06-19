#!/bin/bash


MPIRUN='srun -n 24 -c 2'
SIGMA='sigma.cplx.x'

ln -nfs ../../../01-dft/02-wfn/wfn.cplx WFN_inner
ln -nfs ../../../01-dft/02-wfn/rho.real RHO
ln -nfs ../../../01-dft/02-wfn/vxc.dat vxc.dat
ln -nfs ../../01-epsilon/5.0-ecut/eps0mat.h5 eps0mat.h5
ln -nfs ../../01-epsilon/5.0-ecut/epsmat.h5 epsmat.h5

$MPIRUN $SIGMA &> sigma.out

