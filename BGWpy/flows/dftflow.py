"""Workflow to perform GW calculation."""
from __future__ import print_function

from os.path import join as pjoin

from ..config import dft_flavor, check_dft_flavor
from ..config import is_dft_flavor_espresso, is_dft_flavor_abinit
from ..external import Structure
from ..core import Workflow
from ..BGW import EpsilonTask, SigmaTask
from pymatgen.symmetry.bandstructure import HighSymmKpath

__all__ = ['dftFlow']

class dftFlow(Workflow):
    """
    A one-shot GW workflow made of the following tasks:
        - DFT charge density, wavefunctions and eigenvalues
        - Dielectric Matrix (Epsilon and Epsilon^-1)
        - Self-energy (Sigma)
    """

    def __init__(self, **kwargs):
        """
        Keyword arguments
        -----------------
        (All mandatory unless specified otherwise)

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.
        structure : pymatgen.Structure
            Structure object containing information on the unit cell.
        dft_flavor : 'espresso' | 'abinit'
            Choice of DFT code for density and wavefunctions calculations.
        prefix : str
            Prefix required by QE as a rootname.
        pseudo_dir : str
            Directory in which pseudopotential files are found.
        pseudos : list, str
            Pseudopotential files.
        ngkpt : list(3), float
            K-points grid. Number of k-points along each primitive vector
            of the reciprocal lattice.
        nbnd : int
            Number of bands to be computed.
        ecutwfc : float
            Energy cutoff for the wavefunctions
        kpath : dict, optional
            Any other variables that should be declared in the sigma input file.

        """
        super(dftFlow, self).__init__(**kwargs)

        kwargs.pop('dirname', None)

        self.structure = kwargs['structure']
        self.ngkpt = kwargs.pop('ngkpt')
        self.kshift = kwargs.pop('kshift', [.0,.0,.0])

        nband_aliases = ('nbnd', 'nband')
        for key in nband_aliases:
            if key in kwargs:
                self.nbnd = kwargs.pop(key)
                break
        else:
            raise Exception(
            'Number of bands must be specified with one of these keywords: {}.'
            .format(nband_aliases))

        self.dft_flavor = check_dft_flavor(kwargs.get('dft_flavor',dft_flavor))

        # ==== DFT calculations ==== #

        # Quantum Espresso flavor
        if is_dft_flavor_espresso(self.dft_flavor):
            self.make_dft_tasks_espresso(**kwargs)
            #fnames = self.make_dft_tasks_espresso(**kwargs)
            #kwargs.update(fnames)

        # Abinit flavor
        elif is_dft_flavor_abinit(self.dft_flavor):
            fnames = self.make_dft_tasks_abinit(**kwargs)
            kwargs.update(fnames)

    def make_dft_tasks_espresso(self, **kwargs):
        """
        Initialize all DFT tasks using Quantum Espresso.
        Return a dictionary of file names.
        """
        from ..QE import QeScfTask, QeBgwFlow, QeWfnTask

        # Scf task for bandstructure
        self.scftask = QeScfTask(
            dirname = pjoin(self.dirname, '01-density'),
            ngkpt = self.ngkpt,
            kshift = self.kshift,
            **kwargs)

        self.add_task(self.scftask)
        
        kwargs.update(
            charge_density_fname = self.scftask.charge_density_fname,
            data_file_fname = self.scftask.data_file_fname,
            spin_polarization_fname = self.scftask.spin_polarization_fname)
        
        # Wavefunction tasks for bandstructure (and possibly GW bs) 
        kpoints = HighSymmKpath(self.structure).get_kpoints()[0]
        weights = [1.] * len(kpoints) 

        #kwargs.update(
        #    kpts = kpoints,
        #    wtks = weights)

        self.wfntask = QeWfnTask(
            dirname = pjoin(self.dirname, '02-bandstructure'),
            nbnd = self.nbnd,
            kpts = kpoints,
            wtks = weights,
            **kwargs)

        self.add_task(self.wfntask, merge=False)
        
        #fnames = dict(wfn_co_fname = self.wfntask.wfn_fname) 

        return #fnames

    #def make_dft_tasks_abinit(self, **kwargs):
    #    """
    #    Initialize all DFT tasks using Abinit.
    #    Return a dictionary of file names.
    #    """
    #    from ..Abinit import AbinitScfTask, AbinitBgwFlow

    #    # Either charge density is provided or an SCF task is initialized.
    #    if 'charge_density_fname' in kwargs:
    #        if 'vxc_fname' not in kwargs:
    #            raise Exception("Error, when providing charge_density_fname, vxc_fname is required")

    #    else:
    #        self.scftask = AbinitScfTask(
    #            dirname = pjoin(self.dirname, '01-Density'),
    #            ngkpt = self.ngkpt,
    #            kshift = self.kshift,
    #            **kwargs)

    #        self.add_task(self.scftask)
    #        
    #        kwargs.update(
    #            charge_density_fname = self.scftask.charge_density_fname,
    #            vxc_fname = self.scftask.vxc_fname)

    #    # Option to split the wfn calculation in two calculations,
    #    # where the first one has fewer bands and higher convergence criterion
    #    self.split_wfn = kwargs.pop('split_wfn', False)

    #    # Should the WFN be computed, or are they provided?
    #    self.with_wfn = kwargs.get('with_wfn', True)

    #    if 'wfn_fname' in kwargs:
    #        self.with_wfn = False
    #        wfn_fname = kwargs['wfn_fname']

    #    if 'wfnq_fname' in kwargs:
    #        wfnq_fname = kwargs['wfnq_fname']
    #    elif not self.with_wfn:
    #        raise Exception("When providing wfn_fname, wfnq_fname is also required")

    #    if 'wfn_co_fname' in kwargs:
    #        wfn_co_fname = kwargs['wfn_co_fname']
    #    elif not self.with_wfn:
    #        raise Exception("When providing wfn_fname, wfn_co_fname is also required")

    #    if 'rho_fname' in kwargs:
    #        rho_fname = kwargs['rho_fname']
    #    elif not self.with_wfn:
    #        raise Exception("When providing wfn_fname, rho_fname is required")

    #    if 'vxc_fname' in kwargs:
    #        vxc_fname = kwargs['vxc_fname']
    #    elif not self.with_wfn:
    #        raise Exception("When providing wfn_fname, vxc_fname is required")

    #    # In case wavefunctions are already provided
    #    if not self.with_wfn:
    #        fnames = dict(wfn_fname = wfn_fname,
    #                      wfnq_fname = wfnq_fname,
    #                      wfn_co_fname = wfn_co_fname,
    #                      rho_fname = rho_fname,
    #                      vxc_fname = vxc_fname)

    #        return fnames

    #    # Set number of bands and bands in the buffer,
    #    # specially for cases in which calculation is split into two parts.
    #    nbnd = self.nbnd
    #    if self.split_wfn:
    #        nbnd = kwargs.pop('nband1')
    #        #if nbnd > 30:
    #        #   nbdbuf = 5
    #        #else: 
    #        #   nbdbuf = 0

    #    # Wavefunction tasks for Epsilon
    #    self.wfntask_ksh = AbinitBgwFlow(
    #        dirname = pjoin(self.dirname, '02-Wfn'),
    #        ngkpt = self.ngkpt,
    #        kshift = self.kshift,
    #        nband = nbnd,
    #        #nbdbuf = nbdbuf, #lucky number
    #        rhog_flag = True,
    #        **kwargs)
    #    
    #    self.wfntask_qsh = AbinitBgwFlow(
    #        dirname = pjoin(self.dirname, '03-Wfnq'),
    #        ngkpt = self.ngkpt,
    #        kshift = self.kshift,
    #        qshift = self.qshift,
    #        nband = None,
    #        **kwargs)

    #    self.add_tasks([self.wfntask_ksh, self.wfntask_qsh])

    #    # Add additional WFN task if required
    #    if self.split_wfn:
    #        nbdbuf = int(self.nbnd*0.2)  # 20% of bands are in buffer
    #        self.wfntask_large = AbinitBgwFlow(
    #            dirname = pjoin(self.dirname, '02-Wfn-large'),
    #            ngkpt = self.ngkpt,
    #            kshift = self.kshift,
    #            #qshift = self.qshift,  # GA: I am doubtious about this...
    #            nband = self.nbnd,
    #            nbdbuf = nbdbuf,
    #            tolwfr = "1.d-05",
    #            irdwfk = 1,
    #            input_wavefunction_fname = self.wfntask_ksh.wfn_fname,
    #            **kwargs)


    #    # Unshifted wavefunction tasks for Sigma
    #    # only if not already computed for Epsilon.
    #    if self.has_kshift:

    #        self.wfntask_ush = AbinitBgwFlow(
    #            dirname = pjoin(self.dirname, '04-Wfn_co'),
    #            ngkpt = self.ngkpt,
    #            nband = self.nbnd,
    #            rhog_flag = True,
    #            vxcg_flag = True,
    #            **kwargs)

    #        self.add_task(self.wfntask_ush)

    #    else:
    #        self.wfntask_ush = self.wfntask_ksh

    #    if self.split_wfn:
    #        if self.has_kshift:
    #            raise Exception('Cannot use split_wfn with a k-shift at the moment (to be fixed)')

    #        fnames = dict(wfn_fname = self.wfntask_large.wfn_fname,
    #                      wfnq_fname = self.wfntask_qsh.wfn_fname,
    #                      wfn_co_fname = self.wfntask_large.wfn_fname,
    #                      rho_fname = self.wfntask_large.rho_fname,
    #                      vxc_fname = self.wfntask_large.vxc_fname)
    #    else:
    #        fnames = dict(wfn_fname = self.wfntask_ksh.wfn_fname,
    #                      wfnq_fname = self.wfntask_qsh.wfn_fname,
    #                      wfn_co_fname = self.wfntask_ush.wfn_fname,
    #                      rho_fname = self.wfntask_ush.rho_fname,
    #                      vxc_fname = self.wfntask_ush.vxc_fname)

    #    return fnames
