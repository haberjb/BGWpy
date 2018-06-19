from __future__ import print_function
import os
from copy import copy

from .test_BGW_tasks import TestBGWTasksMaker

from .. import data
from .. import Structure, GWFlow, BSEFlow, convGWFlow

class TestFlows(TestBGWTasksMaker):

    common_kwargs = copy(TestBGWTasksMaker.common_kwargs)
    common_kwargs.update(
        dft_flavor='espresso',
        nbnd_fine=20,
        kshift=[.5,.5,.5],
        qshift = [.001,.0,.0],
        sigma_extra_lines = ['screening_semiconductor'],
        kernel_extra_lines = [
            'use_symmetries_coarse_grid',
            'screening_semiconductor',
            ],
        absorption_extra_lines = [
            'use_symmetries_coarse_grid',
            'no_symmetries_fine_grid',
            'no_symmetries_shifted_grid',
            'screening_semiconductor',
            'use_velocity',
            'gaussian_broadening',
            'eqp_co_corrections',
            ],
        absorption_extra_variables = {
            'energy_resolution' : 0.15,
            },
        chi_cut=[5.0,10.0],
        chi_bands=[10,15],
        sigma_bands=[10,15],
        )

    def get_gwflow(self):
        kwargs = copy(self.common_kwargs)
        return GWFlow(dirname = os.path.join(self.tmpdir, 'GW'), **kwargs)

    def get_bseflow(self):
        kwargs = copy(self.common_kwargs)
        return BSEFlow(dirname = os.path.join(self.tmpdir, 'BSE'), **kwargs)

    def get_convgwflow(self):
        kwargs = copy(self.common_kwargs)
        return convGWFlow(dirname = os.path.join(self.tmpdir, 'convGW'), **kwargs)

    def test_gwflow(self):
        """Test GWFlow."""
        flow = self.get_gwflow()
        flow.write()
        #flow.run()
        flow.report()
        for task in flow.tasks:
            self.assertCompleted(task)
        
    def test_bseflow(self):
        """Test BSEFlow."""
        flow = self.get_bseflow()
        flow.write()
        #flow.run()
        flow.report()
        for task in flow.tasks:
            self.assertCompleted(task)
 
    def test_convgwflow(self):
        """Test convGWFlow."""
        flow = self.get_convgwflow()
        flow.write()
        #flow.run()
        flow.report()
        for task in flow.tasks:
            self.assertCompleted(task)
        
