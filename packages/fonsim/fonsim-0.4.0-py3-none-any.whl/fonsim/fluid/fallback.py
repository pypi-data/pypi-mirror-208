"""
Tool to easily select the most appropriate fallback fluid

2020, September 10
"""


def get_fluid(fluid, fluids_desired):
    """

    :param fluid: Fluid instance
    :param fluids_desired: Ordered iterable (e.g. list, tuple) of Fluid types
    :return: Fluid instance
    """
    if type(fluid) in fluids_desired:
        return fluid
    else:
        lst = list(fluids_desired)
        i = select_fallback(fluid, lst)
        f = lst[i]
        print("Fluid fallback:", fluid, "->", f)
        return f


def select_fallback(fluid, fluids_desired):
    """
    Return given fluid if its type is in fluids_desired.
    Otherwise, from all its fallback fluids
    return the fluid that is first in fluids_desired.

    Note: returns tuple

    :param fluid: fluid object
    :param fluids_desired: ordered iterable (e.g. list, tuple) of fluid types
    :return: (fluid object, index of type of fluid object in fluids_desired)
    """

    # End case: fluid is in the fallback fluids
    # -> return found fluid and its index
    if type(fluid) in fluids_desired:
        index = fluids_desired.index(type(fluid))
        return fluid, index
    # Default case: fluid is not in fallback fluids
    # -> search further in each fallback fluids
    #    and return the result with the lowest index
    else:
        # Collect all (fluid, index) pairs
        a = [select_fallback(f, fluids_desired) for f in fluid.fallbacks]
        # Filter out those that are none
        b = list(filter(lambda x, y: x is not None, a))
        # See if any are left after filtering
        if len(b) > 0:
            # One or more to choose from
            # return the one with the lowest index
            f_s, i_s = zip(*b)
            i = i_s.index(min(i_s))
            f = f_s[i]
            return f, i
        else:
            # None left
            return None, None
