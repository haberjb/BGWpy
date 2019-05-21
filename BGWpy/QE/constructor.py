from .pwscfinput import PWscfInput
from .phscfinput import PHscfInput


def get_scf_input(prefix, pseudo_dir, pseudos, structure, ecutwfc, kpts, wtks):
    """Construct a Quantum Espresso scf input."""
    inp = PWscfInput()
    
    inp.control.update(
        prefix = prefix,
        pseudo_dir = pseudo_dir,
        calculation = 'scf',
        )
    
    inp.electrons.update(
        electron_maxstep = 100,
        conv_thr = 1.0e-10,
        mixing_mode = 'plain',
        mixing_beta = 0.7,
        mixing_ndim = 8,
        diagonalization = 'david',
        diago_david_ndim = 4,
        diago_full_acc = True,
        )
    
    inp.system['ecutwfc'] = ecutwfc,
    inp.set_kpoints_crystal(kpts, wtks)
    inp.structure = structure
    inp.pseudos = pseudos

    return inp


def get_bands_input(prefix, pseudo_dir, pseudos, structure, ecutwfc, kpts, wtks, nbnd=None):
    """Construct a Quantum Espresso bands input."""
    inp = get_scf_input(prefix, pseudo_dir, pseudos, structure, ecutwfc, kpts, wtks)
    inp.control['calculation'] = 'bands'
    if nbnd is not None:
        inp.system['nbnd'] = nbnd
    return inp

def get_ph_input(prefix, pseudo_dir, pseudos, structure, qpts, wtqs):
    """Construct a Quantum Espresso scf input."""
    inp = PHscfInput()

    inp.phonons.update(
        prefix = prefix,
        pseudo_dir = pseudo_dir,
        qplot = True,
        ldisp = True,
        tr2_ph = 1e-16,
        )

    inp.set_qpoints_cart(qpts, wtqs)
    inp.pseudos = pseudos

    return inp
