from __future__ import print_function

import os
import warnings
from numpy import array

from .dfttask import DFTTask
from ..core import Workflow
from ..BGW import KgridTask

# Public
__all__ = ['DFPTTask', 'DFPTFlow']

class DFPTTask(DFTTask):
    """
    Base class for DFT calculations.
    Handles structure, pseudopotentials and k-points grids.
    """

    def __init__(self, dirname, **kwargs):
        """
        Keyword Arguments
        -----------------

        flavor : str ['qe', 'abinit']
            DFT code used for density and wavefunctions.
        pseudo_dir : str
            Path to the directory containing pseudopotential files.
        pseudos : list, str
            List of pseudopotential files.
        """

        super(DFPTTask, self).__init__(dirname, **kwargs)

        # DFPT 
        self.ngqpt     = kwargs.get('ngqpt', [1,1,1])
        self.qgridtask  = KgridTask(dirname=dirname, structure=self.structure, ngkpt=self.ngqpt)

    def get_qpts(self, **kwargs):
        """
        Get the q-points and their weights.

        Keyword Arguments
        -----------------

        symqpt : bool (True)
            Use symmetries to reduce the q-point grid.
        structure : pymatgen.Structure object
            Mandatory if symkpt.
        ngqpt : list(3), float, optional
            Q-points grid. Number of q-points along each primitive vector
            of the reciprocal lattice.
            Q-points are either specified using ngqpt or using qpts and wtqs.
        """

        symqpt = kwargs.get('symqpt', True)

        if 'ngqpt' in kwargs:
            if symqpt:
                qpts, wtqs = self.qgridtask.get_kpoints()
            else:
                qpts, wtqs = self.qgridtask.get_kpt_grid_nosym()
        else:
            qpts, wtqs = kwargs['qpts'], kwargs['wtqs']

        return qpts, wtqs

    @property
    def ngqpt(self):
        return self._ngqpt

    @ngqpt.setter
    def ngqpt(self, ngqpt):
        self._ngqpt = array(ngqpt)

# =========================================================================== #


class DFPTFlow(Workflow, DFPTTask):

    def __init__(self, *args, **kwargs):
        """
        Keyword Arguments
        -----------------

        flavor : str ['qe', 'abinit']
            DFT code used for density and wavefunctions.
        pseudo_dir : str
            Path to the directory containing pseudopotential files.
        pseudos : list, str
            List of pseudopotential files.
        """
        super(DFPTFlow, self).__init__(*args, **kwargs)

        #self.flavor     = kwargs.pop('flavor',  'qe')
        self.pseudo_dir = kwargs.get('pseudo_dir', self.dirname)
        self.pseudos = kwargs.get('pseudos', [])
        self.structure = kwargs.get('structure')

