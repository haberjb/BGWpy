#!/bin/bash


MPIRUN='srun -n 24 -c 2'
EPSILON='epsilon.cplx.x'

ln -nfs ../../01-dft/02-wfn/wfn.cplx WFN
ln -nfs ../../01-dft/03-wfnq/wfn.cplx WFNq

$MPIRUN $EPSILON &> epsilon.out

