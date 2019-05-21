"""
Compute DFT wavefunctions and eigenvalues
on a k-shifted k-point grid,
then adapt them for BGW.

Depends on:
    11-Density
"""
from BGWpy import Structure, QePhTask

task = QePhTask(
    dirname = '41-Phonons',

    structure = Structure.from_file('../../Data/Structures/GaAs.json'),
    prefix = 'GaAs',
    pseudo_dir = '../../Data/Pseudos',
    pseudos = ['31-Ga.PBE.UPF', '33-As.PBE.UPF'],

    ngqpt = [4,4,4],

    groundstate_wfc_dirname = '11-Density/GaAs.save',
    charge_density_fname = '11-Density/GaAs.save/charge-density.dat',
    data_file_fname = '11-Density/GaAs.save/data-file-schema.xml',

    # These are the default parameters for the MPI runner.
    # Please adapt them to your needs.
    nproc = 32,
    nproc_per_node = 2,
    mpirun = 'srun',
    nproc_flag = '-n',
    nproc_per_node_flag = '-c',
    )

# Execution
task.write()
#task.run()
task.report()

