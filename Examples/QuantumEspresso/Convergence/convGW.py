"""
Perform a complete GW calculation including
the DFT wavefunctions, the inverse dielectric matrix, and the self-energy.
"""
from BGWpy import Structure, convGWFlow

flow = convGWFlow(
    dirname='convGW',
    dft_flavor='espresso',

    structure = Structure.from_file('../../Data/Structures/GaAs.json'),
    prefix = 'GaAs',
    pseudo_dir = '../../Data/Pseudos',
    pseudos = ['31-Ga.PBE.UPF', '33-As.PBE.UPF'],

    ecutwfc = 10.0,
    nbnd = 9,

    ngkpt = [2,2,2],
    kshift = [.0,.0,.0],
    qshift = [.001,.0,.0],
    ibnd_min = 1,
    ibnd_max = 8,
    ecuteps = 10.0,

    # Extra lines and extra variables
    epsilon_extra_lines = [],
    epsilon_extra_variables = {},
    sigma_extra_lines = ['screening_semiconductor'],
    sigma_extra_variables = {},

    # Convergence paramters
    chi_cut = [5.0,10.0],
    chi_bands = [10,15],
    sigma_bands = [10,15],

    # Parameters for the MPI runner
    nproc = 24,
    nproc_per_node = 2,
    mpirun = 'srun',
    nproc_flag = '-n',
    nproc_per_node_flag = '-c',
    )


# Execution
flow.write()
#flow.run()
flow.report()
