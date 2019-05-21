
from ..core import fortran_str
from ..core import Writable, Namelist, Card
from .pwscfinput import PWscfInput
import warnings
import numpy as np

class PHscfInput(PWscfInput):

    _structure = None 
    _pseudos = list()

    def __init__(self, **kwargs):

        super(PHscfInput, self).__init__(**kwargs)

        self.phonons = Namelist('inputph')
        self.q_points = Card(None, '')

    def __str__(self):

        # Perform checks
        S = 'QE PHonon calculation\n'
        S += str(self.phonons)
        S += str(self.q_points)

        return S

    def set_qpoints_cart(self, qpts, wtqs):
        self.q_points.append(len(qpts))
        for q, w in zip(qpts, wtqs):
            self.q_points.append(list(q) + [w])
