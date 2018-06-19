#!/bin/bash


MPIRUN='srun -n 24 -c 2'

bash wfn.run.sh
bash pw2bgw.run.sh

