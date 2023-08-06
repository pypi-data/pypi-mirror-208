"""Functions related to generating a distance matrix."""

from itertools import combinations
import pandas as pd
from scipy.spatial.distance import squareform
from weighted_levenshtein import lev
from pytracking_cdm.cost_matrix import cost_matrix
import numpy as np


def distance_matrix(
    df: pd.DataFrame,
    insert_costs_dct: dict = None,
    delete_costs_dct: dict = None,
    substitute_costs_dct: dict = None,
    code_dct: dict = None,
    normalize: bool = False,
) -> np.ndarray:
    """Generate a matrix of levenshtein distances between sequences.

    Params:
    -------
    df:
        pandas dataframe containing one sequence per row
    merge:
        Merge contiguous identical strings.
    insert_costs_dct:
        A dictionary like this: {'label_one': 2}. A string as key and a insertion cost as value.
    delete_costs_dct:
        A dictionary like this: {'label_one': 2}. A string as key and a deletion cost as value.
    substitute_costs_dct:
        A dictionary like this: {'label_one': {"label_two": 1.25}}. The top level dictionary should contain the AOI
        labels as keys and dictionaries as values. The nested dictionaries should contain the aoi label to
        substitute as their keys and the cost of substitution as their values.
    code_dct:
        If your sequences are encoded, but your cost dictionaries are not, also specify a code dictionary.
    normalize:
        Optionally normalize the levenshtein distance by dividing the distance between two strings by the length of the
        longer string

    Returns
    -------
    A matrix of levenshtein distances.

    """
    lst = df.seq.values.tolist()

    insert_costs = cost_matrix(1, insert_costs_dct, code_dct)
    delete_costs = cost_matrix(1, delete_costs_dct, code_dct)

    substitute_costs = cost_matrix(2, substitute_costs_dct, code_dct)

    if normalize:
        distances = [
            lev(i, j, insert_costs=insert_costs, delete_costs=delete_costs, substitute_costs=substitute_costs)
            / max(len(i), len(j))
            for (i, j) in combinations(lst, 2)
        ]
    else:
        distances = [
            lev(i, j, insert_costs=insert_costs, delete_costs=delete_costs, substitute_costs=substitute_costs)
            for (i, j) in combinations(lst, 2)
        ]

    distance_matrix = squareform(distances)
    return distance_matrix
