import ast
from collections import defaultdict
from copy import deepcopy
from functools import reduce
from configparser import ConfigParser
import re
from flatten_any_dict_iterable_or_whatsoever import (
    fla_tu,
    set_in_original_iter,
    ProtectedList,
)
from tolerant_isinstance import isinstance_tolerant
from isiter import isiter

# nested_dict: This variable is a lambda function that creates a nested defaultdict. It is used later to create a nested dictionary structure.
# reg and regint: These variables define regular expression patterns for matching specific patterns in strings.
nested_dict = lambda: defaultdict(nested_dict)
reg = re.compile(r"^[-.,\de+]+", flags=re.I)

regint = re.compile(r"^[-\d+]+", flags=re.I)
from deepcopyall import deepcopy


def load_config_file_vars(cfgfile:str, onezeroasboolean:bool, force_dtypes:dict|None=None):
    """

    """
    pars2 = ConfigParser()
    pars2.read(cfgfile)

    (
        cfgdictcopy,
        cfgdictcopyaslist,
        cfgdictcopysorted,
    ) = copy_dict_and_convert_values(
        pars2, onezeroasboolean=onezeroasboolean, force_dtypes=force_dtypes
    )

    return (
        cfgdictcopy,
        cfgdictcopyaslist,
        cfgdictcopysorted,
    )


def groupby_first_item(
    seq, continue_on_exceptions=True, withindex=False, withvalue=True
):
    return groupBy(
        key=lambda x: x[0],
        seq=seq,
        continue_on_exceptions=continue_on_exceptions,
        withindex=withindex,
        withvalue=withvalue,
    )


def convert_to_normal_dict(di):
    r"""
    Convert a nested defaultdict dictionary to a normal dictionary.

    Args:
        di: The nested defaultdict dictionary.

    Returns:
        The converted normal dictionary.
    """
    if isinstance_tolerant(di, defaultdict):
        di = {k: convert_to_normal_dict(v) for k, v in di.items()}
    return di


def groupBy(key, seq, continue_on_exceptions=True, withindex=True, withvalue=True):
    r"""
    Group items in a sequence based on a key function.

    Args:
        key: A function that defines the grouping key.
        seq: The input sequence to be grouped.
        continue_on_exceptions: Whether to continue grouping even if an exception occurs.
        withindex: Whether to include the index of each item in the group.
        withvalue: Whether to include the value of each item in the group.

    Returns:
        The grouped items as a dictionary.
    """
    indexcounter = -1

    def execute_f(k, v):
        nonlocal indexcounter
        indexcounter += 1
        try:
            return k(v)
        except Exception as fa:
            if continue_on_exceptions:
                return "EXCEPTION: " + str(fa)
            else:
                raise fa

    if withvalue:
        return convert_to_normal_dict(
            reduce(
                lambda grp, val: grp[execute_f(key, val)].append(
                    val if not withindex else (indexcounter, val)
                )
                or grp,
                seq,
                defaultdict(list),
            )
        )
    return convert_to_normal_dict(
        reduce(
            lambda grp, val: grp[execute_f(key, val)].append(indexcounter) or grp,
            seq,
            defaultdict(list),
        )
    )


def check_if_iter_and_return_correct(v):
    """
    Check if a value is iterable and return the first item if iterable.

    Args:
        v: The value to be checked.

    Returns:
        The first item of the iterable if it is iterable, otherwise the original value.
    """
    try:
        if isiter(v, consider_non_iter=(str, bytes)):
            return v[0]
    except Exception:
        pass
    return v


def copy_dict_and_convert_values(pars, onezeroasboolean:bool=False, force_dtypes:dict|None=None):
    r"""
    Copy a ConfigParser object and convert its values to appropriate data types.

    Args:
        pars: The ConfigParser object to be copied and converted.
        onezeroasboolean: Whether to treat 0 and 1 as boolean values.
        force_dtypes: A dictionary mapping keys to specific data types for force-conversion.

    Returns:
        A tuple containing the copied dictionary, a modified list, and a grouped dictionary.
    """
    if not force_dtypes:
        force_dtypes = {}
    copieddict = deepcopy(pars.__dict__["_sections"])
    copieddict2 = deepcopy(copieddict)
    flattli = fla_tu(pars.__dict__["_sections"])
    for value, keys in flattli:
        if keys[-1] in force_dtypes:
            valuewithdtype = force_dtypes[keys[-1]](pars.get(*keys))
        else:
            if not re.search(r"^(?:[01])$", str(value)):
                try:
                    valuewithdtype = pars.getboolean(*keys)
                except Exception:
                    try:
                        valuewithdtype = ast.literal_eval(pars.get(*keys))
                    except Exception as fa:
                        # print(fa)
                        valuewithdtype = pars.get(*keys)
            else:
                if onezeroasboolean:
                    valuewithdtype = pars.getboolean(*keys)
                else:
                    valuewithdtype = ast.literal_eval(pars.get(*keys))

        set_in_original_iter(iterable=copieddict, keys=keys, value=valuewithdtype)
        try:
            if isiter(valuewithdtype, consider_non_iter=(str, bytes)):
                valuewithdtype = ProtectedList([valuewithdtype])
        except Exception:
            pass
        set_in_original_iter(iterable=copieddict2, keys=keys, value=valuewithdtype)

    g = list(fla_tu(copieddict2))
    g2cfg = []
    for new1, new2 in g:
        try:
            if new2[-1][-1] not in force_dtypes:
                if isiter(new1[0], consider_non_iter=(str, bytes)):
                    g2cfg.append((new1[0], new2))
                    continue
        except Exception as fa:
            pass
        g2cfg.append((new1, new2))
    gr = groupby_first_item(
        [(x[1][0], (check_if_iter_and_return_correct(x[0]), x[1])) for x in g]
    )

    return (
        copieddict,
        g2cfg,
        gr,
    )




