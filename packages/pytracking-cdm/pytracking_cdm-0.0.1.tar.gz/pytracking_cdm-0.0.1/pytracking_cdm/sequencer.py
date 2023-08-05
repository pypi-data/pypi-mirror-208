"""Functions related to generating sequences from eyetracking fixations."""

import pandas as pd
import os
from typing import TypeVar

PandasDataFrame = TypeVar("pandas.core.frame.DataFrame")


def sequence(df: pd.DataFrame, aoi_col: str, merge: bool = False) -> str:
    """Convert fixations to a single sequence.

    Params:
    ------
    df: Dataframe containing row wise fixations.
    aoi_col: Column that contains the label of the fixation/area of interest.
    merge: Merge contiguous identical strings.

    Returns
    -------
    A sequence as a joined string.

    """
    df[aoi_col] = df[aoi_col].astype(str)

    seq = df[aoi_col].str.cat(sep="")

    if merge:
        lst = [*seq]
        temp = []
        for count, i in enumerate(lst):
            if count != len(lst) - 1:
                if lst[count + 1] != i:
                    temp.append(i)
            else:
                temp.append(i)
        seq = "".join(temp)

    return seq


def ascii_to_char(code: int) -> str:
    """Convert an integer (which equals asci code, but shifted by 33) to a character.

    Params:
    ------
    code: The asci code.

    Returns
    -------
    An ASCII character .

    """
    # Excluding control characters
    start = 33
    code = code + start
    if code < 33 or code > 126:
        raise ValueError("Code must be between 33 and 126")
    return chr(code)


def gen_code_dct(df: pd.DataFrame, aoi_col: str, code_dct: dict = {}) -> dict:
    """Generate or append a dictionary that assigns existing AOI labels a code in the form of an ASCII string.

    Params:
    ------
    df: Dataframe containing row wise fixations.
    aoi_col: Column that contains the label of the area of interest.
    code_dct: Input an existing code dictionary to append it.

    Returns
    -------
    A dicionary with the AOI labels as keys and their encodings as values.

    """
    # get unique items that are not already in the code dictionary
    new_unique_aoi = [x for x in df[aoi_col].unique().tolist() if x not in code_dct.keys()]
    lock = len(code_dct.keys())
    # if there are new items, iteratively add new items but shift the asci integer by the length of the old code
    # dictionary
    if len(new_unique_aoi) != 0:
        for lst_count, i in enumerate(new_unique_aoi):
            code_dct[i] = ascii_to_char(lock + lst_count)
    return code_dct


def sequencer(
    folder: str, id_col: str, aoi_col: str, off_aoi_str: str = None, sep_col: str = None, merge: bool = False
) -> [pd.DataFrame, dict]:
    """Convert a folder of files containing row wise fixations to a dataframe of sequences.

    Params:
    ------
    folder: Input folder containing files of rowise fixations as csv per individual or trial.
    id_col: Name of the column containing the unique id of the individual or trial.
    aoi_col: Name of the column containing the AOI labels.
    off_aoi_str: Exclude the AOIs with this label when generating the sequences. This is usually the label for a
    fixation that's not on an area of interest.
    sep_col: A column that contains some category (for example trials) that should be treated as separate sequences.
    merge: Merge contiguous identical strings.

    Return
    ------
    A pandas dataframe of one sequence per row per individual or trial, depending on params and a dictionary with the
    aoi labels as keys and their encoded sequence chars as values.

    """
    seq_lst = []
    id_lst = []
    length_lst = []
    code_dct = dict()

    # iterate over files in folder
    with os.scandir(folder) as it:
        # sort by name (mainly for testing)
        for entry in sorted(it, key=lambda e: e.name):
            df = pd.read_csv(entry.path)

            # delete all rows containing off_aoi_str
            if off_aoi_str is not None:
                df = df[df[aoi_col] != off_aoi_str]

            # generate or append a code dictionary
            code_dct = gen_code_dct(df, aoi_col, code_dct)

            # convert the aoi_col to the encoded chars
            df[aoi_col] = df[aoi_col].apply(lambda x: code_dct[x])

            # if a file should not be into sep. sequences
            if sep_col is not None:
                # generare a list of sep. dfs corresponding to sep_col
                df_lst = [y for x, y in df.groupby(sep_col)]
                for df in df_lst:
                    # for each df, generate a sequence, measure length of sequence and add both plus the id
                    # (appended by sep_col) to lists
                    seq = sequence(df, aoi_col=aoi_col, merge=merge)
                    seq_lst.append(seq)
                    length_lst.append(len(seq))
                    # TODO handle same id/trial in different files
                    id_lst.append(f"{df[id_col].iloc[0]}_{df[sep_col].iloc[0]}")

            else:
                # same as above but without appending id
                seq = sequence(df, aoi_col=aoi_col, merge=merge)
                length_lst.append(len(seq))
                seq_lst.append(seq)
                # TODO handle same id in different files
                id_lst.append(df[id_col].iloc[0])

    # generate pandas df out of the lists
    df = pd.DataFrame({"id": id_lst, "seq": seq_lst, "len": length_lst})
    df.id = df.id.astype(str)
    return [df, code_dct]
