from __future__ import print_function
import os
import numpy as np

from .qedfpttask      import QeDFPTTask
from .constructor import get_ph_input

# Public
__all__ = ['QePhTask']


class QePhTask(QeDFPTTask):
    """DFPT calculation."""

    _TASK_NAME = 'Ph'

    _input_fname = 'ph.in'
    _output_fname = 'ph.out'

    def __init__(self, dirname, **kwargs):
        """
        Arguments
        ---------

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.


        Keyword arguments
        -----------------
        (All mandatory unless specified otherwise)

        prefix : str
            Prefix required by QE as a rootname.
        pseudo_dir : str
            Directory in which pseudopotential files are found.
        pseudos : list, str
            Pseudopotential files.
        structure : pymatgen.Structure
            Structure object containing information on the unit cell.
        ecutwfc : float
            Energy cutoff for the wavefunctions
        nbnd : int, optional
            Number of bands to be computed.
        charge_density_fname : str
            Path to the charge density file produced
            by a density calculation ('charge-density.dat').
        data_file_fname : str
            Path to the xml data file produced 
            by a density calculation ('data-file.xml').
        spin_polarization_fname : str, optional
            Path to the spin polarization file produced
            by a density calculation ('spin-polarization.dat').
        ngkpt : list(3), float, optional
            K-points grid. Number of k-points along each primitive vector
            of the reciprocal lattice.
            K-points are either specified using ngkpt or using kpts and wtks.
        kshift : list(3), float, optional
            Relative shift of the k-points grid along each direction,
            as a fraction of the smallest division along that direction.
        qshift : list(3), float, optional
            Absolute shift of the k-points grid along each direction.
        symkpt : bool (True), optional
            Use symmetries for the k-point grid generation.
        kpts : 2D list(nkpt,3), float, optional
            List of k-points.
            K-points are either specified using ngkpt or using kpts and wtks.
        wtks : list(nkpt), float, optional
            Weights of each k-point.

        """

        super(QePhTask, self).__init__(dirname, **kwargs)
        self.add_pseudos_copy()

        self.runscript['PH'] = kwargs.get('PH', 'ph.x')
        self.runscript['PHFLAGS'] = kwargs.get('PHFLAGS', '')

        # In QE qpts must be specified in cartesian coordinates..
        qpts, wtqs = self.get_qpts(**kwargs)
        a = self.structure.lattice.a
        blat = self.structure.lattice.reciprocal_lattice_crystallographic.matrix * a
        b_inv = np.linalg.inv(blat)
        np.dot(b_inv

        self.charge_density_fname = kwargs['charge_density_fname']

        # For DFPT calcualtion, in addition to charge_density, the dft wavefunctions
        self.groundstate_wfc_dirname = kwargs['groundstate_wfc_dirname']

        if 'spin_polarization_fname' in kwargs:
            self.spin_polarization_fname = kwargs['spin_polarization_fname']

        self.data_file_fname = kwargs['data_file_fname']

        # Input file
        self.input = get_ph_input(
            self.prefix,
            self.pseudo_dir,
            self.pseudos,
            self.structure,
            qpts,
            wtqs,
            )

        if 'variables' in kwargs:
            self.input.set_variables(kwargs['variables'])

        self.input.fname = self._input_fname

        # Run script
        self.runscript.append('$MPIRUN $PH $PHFLAGS -in {} &> {}'.format(
                              self._input_fname, self._output_fname))

    @property
    def charge_density_fname(self):
        return self._charge_density_fname

    @charge_density_fname.setter
    def charge_density_fname(self, value):
        self._charge_density_fname = value
        dest = os.path.join(self.savedir, 'charge-density.dat')
        self.update_link(value, dest)

    # For DFPT, we need to link the wavefunctions from either scf 
    # or nscf calcualtion.
    @property
    def groundstate_wfc_dirname(self):
        return self._groundstate_wfc_dirname

    @groundstate_wfc_dirname.setter
    def groundstate_wfc_dirname(self, value):
        self._groundstate_wfc_dirname = value
        for wfc_file in os.listdir(value):
            if wfc_file.startswith('wfc'):
                orig = os.path.join(value, wfc_file)
                dest = os.path.join(self.savedir, wfc_file)
                self.update_link(orig, dest)

    @charge_density_fname.setter
    def charge_density_fname(self, value):
        self._charge_density_fname = value
        dest = os.path.join(self.savedir, 'charge-density.dat')
        self.update_link(value, dest)

    @property
    def spin_polarization_fname(self):
        return self._spin_polarization_fname

    @spin_polarization_fname.setter
    def spin_polarization_fname(self, value):
        self._spin_polarization_fname = value
        dest = os.path.join(self.savedir, 'spin-polarization.dat')
        self.update_link(value, dest)

    @property
    def data_file_fname(self):
        return self._data_file_fname

    @data_file_fname.setter
    def data_file_fname(self, value):
        self._data_file_fname = value
        if self.version >= 6.2:
            dest = os.path.join(self.savedir, 'data-file-schema.xml')
        else:
            dest = os.path.join(self.savedir, 'data-file.xml')
        self.update_copy(value, dest)

    def add_pseudos_copy(self):
        """
        Add instructions in the runscript to copy the pseudopotential files.
        This is necessary, because otherwise, Quantum Espresso expect that
        the relative path for the pseudopotential directory be the same
        for the wavefunction calculation as for the density calculation.
        """
        if os.path.realpath(self.pseudo_dir) == self.pseudo_dir.rstrip(os.path.sep):
            sourcedir = self.pseudo_dir
        else:
            sourcedir = os.path.join(self.dirname, self.pseudo_dir)
        for pseudo in self.pseudos:
            source = os.path.join(sourcedir, pseudo)
            dest = os.path.join(self.savedir, pseudo)
            self.update_copy(source, dest)

    # Yikes! I have to recopy the property. python3 would be so much better...
    @property
    def pseudo_dir(self):
        return self._pseudo_dir

    @pseudo_dir.setter
    def pseudo_dir(self, value):
        if os.path.realpath(value) == value.rstrip(os.path.sep):
            self._pseudo_dir = value
        else:
            self._pseudo_dir = os.path.relpath(value, self.dirname)
        if 'input' in dir(self):
            if 'control' in dir(self.input):
                self.input.control['pseudo_dir'] = self._pseudo_dir
        if 'pseudos' in dir(self):
            self.add_pseudos_copy()
