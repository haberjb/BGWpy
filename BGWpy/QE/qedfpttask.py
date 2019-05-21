from __future__ import print_function

import os

from ..core.util import exec_from_dir
from ..core import MPITask, IOTask
from ..DFT import DFPTTask

# Public
__all__ = ['QeDFPTTask']


class QeDFPTTask(DFPTTask, IOTask):
    """Base class for Quantum Espresso calculations."""

    _TAG_JOB_COMPLETED = 'JOB DONE'

    def __init__(self, dirname, **kwargs):
        """
        Arguments
        ---------

        dirname : str
            Directory in which the files are written and the code is executed.
            Will be created if needed.

        Keyword arguments
        -----------------

        See also:
            BGWpy.DFT.DFTTask

        """

        super(QeDFPTTask, self).__init__(dirname, **kwargs)

        self.prefix = kwargs['prefix']
        self.savedir = self.prefix + '.save'

    def exec_from_savedir(self):
        original = os.path.realpath(os.curdir)
        if os.path.realpath(original) == os.path.realpath(self.dirname):
            return exec_from_dir(self.savedir)
        return exec_from_dir(os.path.join(self.dirname, self.savedir))

    def write(self):
        self.check_pseudos()
        super(QeDFPTTask, self).write()
        with self.exec_from_dirname():
            self.input.write()
            if not os.path.exists(self.savedir):
                os.mkdir(self.savedir)

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

