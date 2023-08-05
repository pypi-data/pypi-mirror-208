from pykingas import MieType, cpp_LJSpline
import numpy as np
from scipy.constants import Boltzmann
from thermopack.ljs_wca import ljs_wca
import warnings

class LJSpline(MieType.MieType):

    def __init__(self, comps, 
                mole_weights=None, sigma=None, eps_div_k=None, kij=0, lij=0,
                N=1, is_idealgas=False,
                parameter_ref='default'):

        warnings.warn('Lennard-Jones Spline potential is untested!')

        if is_idealgas is False:
            warnings.warn('Radial distribution function for LJs is not implemented!\n'
                          'The rdf. is required for non-ideal gas solutions. I am\n'
                          'setting is_idealgas=True and giving you this warning instead\n'
                          'of throwing an error.',
                          RuntimeWarning, stacklevel=2)
            is_idealgas=True

        super().__init__(comps, 'LJs',
                        mole_weights=mole_weights, sigma=sigma, eps_div_k=eps_div_k,
                        la=None, lr=None, lij=lij, kij=kij,
                        N=N, is_idealgas=is_idealgas, parameter_ref=parameter_ref)
        self.cpp_kingas = cpp_LJSpline(self.mole_weights, self.sigma_ij, self.epsilon_ij, self.is_idealgas)
        self.eos = ljs_wca()
        self.eos.init()
