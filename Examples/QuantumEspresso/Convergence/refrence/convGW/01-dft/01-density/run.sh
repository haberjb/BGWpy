#!/bin/bash


MPIRUN='srun -n 24 -c 2'
PW='pw.x'
PWFLAGS=''
PH='ph.x'
PHFLAGS=''

$MPIRUN $PW $PWFLAGS -in scf.in &> scf.out

