# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-11 23:25:36
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Regular methods.
"""


from typing import List, Tuple, Optional, Union, Literal, overload
from re import search as _re_search, sub as _re_sub


def re_search(pattern: str, text: str) -> Optional[Union[str, Tuple[Optional[str], ...]]]:
    """
    Regular `matching` text.

    Parameters
    ----------
    pattern : Regular pattern.
    text : Match text.

    Returns
    -------
    Matching result.
        - When match to and not use group, then return string.
        - When match to and use group, then return tuple with value string or None.
        - When no match, then return.
    """

    # Search.
    obj_re = _re_search(pattern, text)

    # Return result.
    if obj_re != None:
        result = obj_re.groups()
        if result == ():
            result = obj_re[0]
        return result


@overload
def res_search(text: str, *patterns: str, first: bool = True) -> Union[
    Optional[Union[str, Tuple[Optional[str], ...]]],
    List[Optional[Union[str, Tuple[Optional[str], ...]]]]
]: ...

@overload
def res_search(first: Literal[True]) -> Optional[Union[str, Tuple[Optional[str], ...]]]: ...

@overload
def res_search(first: Literal[False]) -> List[Optional[Union[str, Tuple[Optional[str], ...]]]]: ...

def res_search(text: str, *patterns: str, first: bool = True) -> Union[
    Optional[Union[str, Tuple[Optional[str], ...]]],
    List[Optional[Union[str, Tuple[Optional[str], ...]]]]
]:
    """
    `Batch` regular `matching` text.

    Parameters
    ----------
    text : Match text.
    pattern : Regular pattern.
    first : Whether return first successful match.

    Returns
    -------
    Matching result.
        - When match to and not use group, then return string.
        - When match to and use group, then return tuple with value string or None.
        - When no match, then return.
    """

    # Search.

    ## Return first result.
    if first:
        for pattern in patterns:
            result = re_search(pattern, text)
            if result != None:
                return result

    ## Return all result.
    else:
        result = [re_search(pattern, text) for pattern in patterns]
        return result

def res_sub(text: str, *patterns: Tuple[str, str]) -> str:
    """
    `Batch` regular `subbing` text.

    Parameters
    ----------
    text : Match text.
    pattern : Regular pattern and replace text.

    Returns
    -------
    Subbing result.
    """

    # Sub.
    for pattern, replace in patterns:
        text = _re_sub(pattern, replace, text)

    return text