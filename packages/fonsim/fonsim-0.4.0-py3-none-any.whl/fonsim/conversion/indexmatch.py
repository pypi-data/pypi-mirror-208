"""
Get index of best-matching labels

2020, September 4
"""

import difflib

import numpy as np


def similar(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


def get_index_of_best_match(unit, candidates):
    """
    Get index of best-matching labels

    Note: all labels are converted to strings and lowercase

    :param unit: base label to compare with
    :param candidates: list of labels to compare against and get index from
    :return: index of best match
    """
    u = str(unit.lower())
    scores = [similar(u, str(c).lower()) for c in candidates]
    #print("scores:", scores)
    i = np.argmax(scores)

    # Notify user of the made match
    # if the two strings in lowercase to not match.
    candidate_chosen = candidates[i]
    if candidate_chosen.lower() != unit.lower():
        print('automatch: "' + unit + '" -> "' + candidate_chosen + '"')

    return i
