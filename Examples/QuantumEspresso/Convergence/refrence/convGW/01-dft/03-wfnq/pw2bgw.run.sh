#!/bin/bash


MPIRUN='srun -n 24 -c 2'
PW='pw.x'
PWFLAGS=''
PH='ph.x'
PHFLAGS=''
PW2BGW='pw2bgw.x'

$MPIRUN $PW2BGW -in wfn.pp.in &> wfn.pp.out

