"""Functions related to generating a cost_matrix."""

import numpy as np


def cost_matrix(dim: int, dct: dict, code_dct: dict = None) -> np.ndarray:
    """Generate a matrix of costs.

    Params:
    ------
    dim:
        whether the inputted dictionary is flat (delete costs or insert costs) or nestes (substitute costs)
    dct:
        the dictionary containing the costs
    code_dct:
        Optionally input a code dictionary if you want to encode the cost matrix

    Returns
    -------
    A numpy 128 or 128 by 128 long 1 or 2 dim array. The indexes correspond to ASCII codes and the values to costs.

    Usage:
    ------
    >>> from pytracking_cdm.cost_matrix import cost_matrix
    >>> cost_matrix(1, {"1": 2}, code_dct)
    """
    if dim == 1:
        # 1 dim matrix of ones (standard cost). Length is 128 because of ASCII (all possible labels)
        costs = np.ones(128, dtype=np.float64)
        if dct is None:
            return costs
        # for every item in cost dict
        for key, value in dct.items():
            # encode or not
            if code_dct is None:
                # ord converts a character to its asci value
                costs[ord(key)] = value
            else:
                costs[ord(code_dct[key])] = value
        return costs
    elif dim == 2:
        # 2 dim matrix of ones (standard cost).
        costs = np.ones((128, 128), dtype=np.float64)
        if dct is None:
            return costs
        # for every item in cost dict
        for key, value in dct.items():
            # for every item corresponding to top level key in cost dict
            for key2, value2 in value.items():
                # encode or not
                if code_dct is None:
                    costs[ord(key), ord(key2)] = value2
                else:
                    costs[ord(code_dct[key]), ord(code_dct[key2])] = value2
    return costs
