"""
2022, May 12
"""

from ..core.variable import *
import fonsim.constants.norm as cnorm

terminal_fluidic = [
    Variable('pressure', 'across',
             initial_value=cnorm.pressure_atmospheric, range=(0, np.Inf)),
    Variable('massflow', 'through', initial_value=0)
]
