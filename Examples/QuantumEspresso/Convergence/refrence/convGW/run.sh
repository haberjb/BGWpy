#!/bin/bash



cd 01-dft/01-density
bash run.sh
cd ../..
cd 01-dft/02-wfn
bash run.sh
cd ../..
cd 01-dft/03-wfnq
bash run.sh
cd ../..
cd 02-conv-sigma-bands/01-epsilon
bash run.sh
cd ../..
cd 02-conv-sigma-bands/02-sigma/10-bands
bash run.sh
cd ../../..
cd 02-conv-sigma-bands/02-sigma/15-bands
bash run.sh
cd ../../..
cd 03-conv-chi-bands/01-epsilon/10-bands
bash run.sh
cd ../../..
cd 03-conv-chi-bands/02-sigma/10-bands
bash run.sh
cd ../../..
cd 03-conv-chi-bands/01-epsilon/15-bands
bash run.sh
cd ../../..
cd 03-conv-chi-bands/02-sigma/15-bands
bash run.sh
cd ../../..
cd 04-conv-chi-cut/01-epsilon/5.0-ecut
bash run.sh
cd ../../..
cd 04-conv-chi-cut/02-sigma/5.0-ecut
bash run.sh
cd ../../..
cd 04-conv-chi-cut/01-epsilon/10.0-ecut
bash run.sh
cd ../../..
cd 04-conv-chi-cut/02-sigma/10.0-ecut
bash run.sh
cd ../../..

