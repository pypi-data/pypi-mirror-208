"""
Fluid classes for keeping fluid properties

Currently supported types:

- IdealIncompressible

  - newtonian
- IdealCompressible

  - newtonian, ideal gas

Types in progress:

- Bingham
  - example of a non-newtonian one

2019, September 7
"""

from . import fallback


# Fluid class
class Fluid:
    """
    :param name: name of fluid
    """
    def __init__(self, name):
        self.name = str(name)
        self.fallbacks = []

    def __str__(self):
        string = "fluid <" + self.name + ">, fallbacks: "
        if len(self.fallbacks) > 0:
            for f in self.fallbacks:
                string += "<" + f.name + ">, "
        else:
            string += "None"
        return string

    def select_object_by_fluid(self, object_by_fluids_compatible):
        """
        Rely on fluid fallback functionality.

        Note: select_fallback expects an ordered iterable
        by making it a list the dict fluids_desired becomes ordered,
        yet a dict has no order of it keys. The made order is thus
        not the same as the one defined in the components.

        Solution: use OrderedDict in the component definition,
        those remember the order of the keys like they were defined.

        The function does not crash when giving a standard Dict,
        but it won't be able to respect the order.

        :param object_by_fluids_compatible: OrderedDict with (type(fluid), object) pairs
        :return: object
        """
        # Use fallback tool to get compatible fluid
        fd = fallback.get_fluid(self, object_by_fluids_compatible.keys())
        # Get object
        obj = object_by_fluids_compatible[type(fd)]
        return obj


class IdealIncompressible(Fluid):
    """
    :param name: name of fluid
    :param rho: density [kg/m**3]
    :param mu: dynamic viscosity [Pa s]
    """
    def __init__(self, name, rho, mu):
        Fluid.__init__(self, name)
        self.rho = rho
        self.mu = mu


class IdealCompressible(Fluid):
    """
    :param name: name of fluid
    :param rho: density at STP conditions [kg/m**3]
    :param mu: dynamic viscosity [Pa s]
    :param fallback: fallback fluid
    """
    def __init__(self, name, rho, mu, fallbacks=None):
        Fluid.__init__(self, name)
        self.rho_stp = rho
        self.mu = mu

        # Incompressible approximation
        if fallbacks is None:
            self.fallbacks = [IdealIncompressible(name=self.name+'_incompressible', mu=self.mu, rho=self.rho_stp)]
        else:
            self.fallbacks = list(fallbacks)


class Bingham:
    """
    Note: in progress!

    :param name: name of fluid
    :param rho: density [kg/m**3]
    :param mu_p: plastic viscosity [Pa s] (sometimes called Poise, [P])
    :param tau_y: yield point (YP) (yield shear stress) [Pa]
    :param fallback: fallback fluid
    """
    def __init__(self, name, rho, mu_p, tau_y, fallbacks=None):
        Fluid.__init__(self, name)
        self.rho = rho
        self.mu_p = mu_p
        self.tau_y = tau_y

        # Newtonian approximation
        if fallbacks is None:
            # Approximate kinematic viscosity
            nu_approx = self.mu_p/self.rho
            self.fallbacks = [IdealIncompressible(name=self.name+'_newtonian', nu=nu_approx, rho=self.rho)]
        else:
            self.fallbacks = list(fallbacks)
