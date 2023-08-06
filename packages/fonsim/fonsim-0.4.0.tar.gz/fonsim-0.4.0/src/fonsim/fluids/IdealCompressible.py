"""
Some common compressible fluids at T = 20 °C, p = 1 bar.
These fluids are described as an ideal gas.

Available:
 - air

In progress:
 - helium (H2)
 - nitrogen (N2)
 - carbondioxide (CO2)
 - oxygen (O2)

2020, September 9
"""

from fonsim.fluid import fluid

# Source: http://www.mhtl.uwaterloo.ca/old/onlinetools/airprop/airprop.html
air = fluid.IdealCompressible(name="air", rho=1.23, mu=1.82e-5)
'''
helium = fluid.IdealCompressible(name="helium", rho=0.167, nu=1.17e-4)
nitrogen = fluid.IdealCompressible(name="nitrogen", rho=1.17, nu=1.51e-5)
carbondioxide = fluid.IdealCompressible(name="carbondioxide", rho=1.81, nu=8.1e-6)

# Source: https://www.engineeringtoolbox.com/
oxygen = fluid.IdealCompressible(name="oxygen", rho=1.31, nu=1.54e-5)
'''
