"""
Some common incomressible fluids at T = 20 °C, p = 1 bar.

Available:
 - water

In progress:
 - ethylene_glycol
 - ethylene_glycol_30pct
 - ethylene_glycol_50pct
 - mineral_oil

2020, September 9
"""

from fonsim.fluid import fluid

# Source: http://www.mhtl.uwaterloo.ca/old/onlinetools/airprop/airprop.html
water = fluid.IdealIncompressible(name="water", rho=999, mu=9.77e-4)
'''
ethylene_glycol = fluid.IdealIncompressible(name="ethylene glycol", rho=1116, nu=1.91e-5)
ethylene_glycol_30pct = fluid.IdealIncompressible(name="ethylene glycol 30%", rho=1038, nu=2.089e-6)
ethylene_glycol_50pct = fluid.IdealIncompressible(name="ethylene glycol 50%", rho=1056, nu=3.66e-6)

# Source: http://www.fao.org/fileadmin/user_upload/jecfa_additives/docs/monograph13/additive-527-m13.pdf
mineral_oil = fluid.IdealIncompressible(name="mineral oil", rho=850, nu=9.75e-4)
'''
