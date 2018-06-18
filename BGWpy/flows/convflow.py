"""Workflow to perform GW calculation."""
from __future__ import print_function

from os.path import join as pjoin

from ..config import dft_flavor, check_dft_flavor
from ..config import is_dft_flavor_espresso, is_dft_flavor_abinit
from ..external import Structure
from ..core import Workflow
from ..BGW import EpsilonTask, SigmaTask

__all__ = ['convFlow']

class convFlow(Workflow):
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
        chi_cut : list
            List of cutoffs to be used when truncating chi.
        chi_bands : list
            List of number of bands for converging chi with respect to.
        sigma_bands : list
            List of number bands for converging sigma with respect to.
        """

        super(convFlow, self).__init__(**kwargs)

        kwargs.pop('dirname', None)

        self.structure = kwargs['structure']
        self.ngkpt = kwargs.pop('ngkpt')
        self.kshift = kwargs.pop('kshift', [.0,.0,.0])
        self.qshift = kwargs.pop('qshift', [.0,.0,.0])

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
            fnames = self.make_dft_tasks_espresso(**kwargs)
            kwargs.update(fnames)

        # Abinit flavor
        elif is_dft_flavor_abinit(self.dft_flavor):
            fnames = self.make_dft_tasks_abinit(**kwargs)
            kwargs.update(fnames)

        # ==== GW calculations ==== #  
        
        # Set some common variables for Epsilon and Sigma
        self.epsilon_extra_lines = kwargs.pop('epsilon_extra_lines', [])
        self.epsilon_extra_variables = kwargs.pop('epsilon_extra_variables',{})
        self.chi_bands = kwargs.pop('chi_bands', [])
        self.chi_cut = kwargs.pop('chi_cut', [])
        
        self.sigma_extra_lines = kwargs.pop('sigma_extra_lines', [])
        self.sigma_extra_variables = kwargs.pop('sigma_extra_variables', {})
        self.sigma_bands = kwargs.pop('sigma_bands', [])

        # ==== Converge w/r to bands in Sigma === #

        # Set up dielectric matrix computation
        self.epsilon_extra_variables.update({'number_bands' : self.chi_bands[-1]})

        self.epsilontask = EpsilonTask(
            dirname = pjoin(self.dirname, '02-conv-sigma-bands/01-epsilon'),
            ngkpt = self.ngkpt,
            qshift = self.qshift,
            extra_lines = self.epsilon_extra_lines,
            extra_variables = self.epsilon_extra_variables,
            ecuteps = self.chi_cut[-1],
            **kwargs)
        self.add_tasks([self.epsilontask], merge=False)

        # Set up Sigma computations for increasing number of bands
        for nb in self.sigma_bands:
            self.sigma_extra_variables.update({'number_bands' : nb})

            self.sigmatask = SigmaTask(
                dirname = pjoin(self.dirname, '02-conv-sigma-bands/02-sigma', '{}-bands'.format(nb)),
                ngkpt = self.ngkpt,
                extra_lines = self.sigma_extra_lines,
                extra_variables = self.sigma_extra_variables,
                eps0mat_fname = self.epsilontask.eps0mat_fname,
                epsmat_fname = self.epsilontask.epsmat_fname,
                **kwargs)
            self.add_tasks([self.sigmatask], merge=False)


        # ==== Converge w/r to bands in Chi === #

        # Set up dielectric matrix computation for increasing number of bands
        self.sigma_extra_variables.update({'number_bands' : self.sigma_bands[-1]}) 

        for nb in self.chi_bands:
            self.epsilon_extra_variables.update({'number_bands' : nb})

            self.epsilontask = EpsilonTask(
                dirname = pjoin(self.dirname, '03-conv-chi-bands/01-epsilon', '{}-bands'.format(nb)),
                ngkpt = self.ngkpt,
                qshift = self.qshift,
                extra_lines = self.epsilon_extra_lines,
                extra_variables = self.epsilon_extra_variables,
                ecuteps = self.chi_cut[-1],
                **kwargs)

            # Set up Sigma computations for increasing number of bands
            self.sigmatask = SigmaTask(
                dirname = pjoin(self.dirname, '03-conv-chi-bands/02-sigma', '{}-bands'.format(nb)),
                ngkpt = self.ngkpt,
                extra_lines = self.sigma_extra_lines,
                extra_variables = self.sigma_extra_variables,
                eps0mat_fname = self.epsilontask.eps0mat_fname,
                epsmat_fname = self.epsilontask.epsmat_fname,
                **kwargs)

            self.add_tasks([self.epsilontask, self.sigmatask], merge=False)

        # ==== Converge w/r to epscut in Chi  === #

        self.epsilon_extra_variables.update({'number_bands' : self.chi_bands[-1]})
        self.sigma_extra_variables.update({'number_bands' : self.sigma_bands[-1]})

        for ecut in self.chi_cut:
            # Set up dielectric matrix computation for increasing number of bands
            self.epsilontask = EpsilonTask(
                dirname = pjoin(self.dirname, '04-conv-chi-cut/01-epsilon', '{}-ecut'.format(ecut)),
                ngkpt = self.ngkpt,
                qshift = self.qshift,
                extra_lines = self.epsilon_extra_lines,
                extra_variables = self.epsilon_extra_variables,
                ecuteps = ecut,
                **kwargs)

            # Set up Sigma computations for increasing number of bands
            self.sigmatask = SigmaTask(
                dirname = pjoin(self.dirname, '04-conv-chi-cut/02-sigma', '{}-ecut'.format(ecut)),
                ngkpt = self.ngkpt,
                extra_lines = self.sigma_extra_lines,
                extra_variables = self.sigma_extra_variables,
                eps0mat_fname = self.epsilontask.eps0mat_fname,
                epsmat_fname = self.epsilontask.epsmat_fname,
                **kwargs)

            self.add_tasks([self.epsilontask, self.sigmatask], merge=False)


    def make_dft_tasks_espresso(self, **kwargs):
        """
        Initialize all DFT tasks using Quantum Espresso.
        Return a dictionary of file names.
        """
        from ..QE import QeScfTask, QeBgwFlow

        if 'charge_density_fname' in kwargs:
            if 'data_file_fname' not in kwargs:
                raise Exception("Error, when providing charge_density_fname, data_file_fname is required.")

        else:

            self.scftask = QeScfTask(
                dirname = pjoin(self.dirname, '01-dft/01-density'),
                ngkpt = self.ngkpt,
                kshift = self.kshift,
                **kwargs)

            self.add_task(self.scftask)
            
            kwargs.update(
                charge_density_fname = self.scftask.charge_density_fname,
                data_file_fname = self.scftask.data_file_fname,
                spin_polarization_fname = self.scftask.spin_polarization_fname)
        
        # Wavefunction tasks for Epsilon
        self.wfntask_ksh = QeBgwFlow(
            dirname = pjoin(self.dirname, '01-dft/02-wfn'),
            ngkpt = self.ngkpt,
            kshift = self.kshift,
            nbnd = self.nbnd,
            rhog_flag = True,
            **kwargs)

        self.wfntask_qsh = QeBgwFlow(
            dirname = pjoin(self.dirname, '01-dft/03-wfnq'),
            ngkpt = self.ngkpt,
            kshift = self.kshift,
            qshift = self.qshift,
            nbnd = None,
            **kwargs)

        self.add_tasks([self.wfntask_ksh, self.wfntask_qsh])

        # Unshifted wavefunction tasks for Sigma
        # only if not already computed for Epsilon.
        #if self.has_kshift:

        #    self.wfntask_ush = QeBgwFlow(
        #        dirname = pjoin(self.dirname, '04-wfn_co'),
        #        ngkpt = self.ngkpt,
        #        nbnd = self.nbnd,
        #        rhog_flag = True,
        #        **kwargs)

        #    self.add_task(self.wfntask_ush)

        #else:
        self.wfntask_ush = self.wfntask_ksh

        fnames = dict(wfn_fname = self.wfntask_ksh.wfn_fname,
                      wfnq_fname = self.wfntask_qsh.wfn_fname,
                      wfn_co_fname = self.wfntask_ush.wfn_fname,
                      rho_fname = self.wfntask_ush.rho_fname,
                      vxc_dat_fname = self.wfntask_ush.vxc_dat_fname)

        return fnames
