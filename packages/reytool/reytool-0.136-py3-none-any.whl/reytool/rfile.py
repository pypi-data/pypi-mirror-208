# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-05-09 15:30:10
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : File methods.
"""


from typing import Union, Literal, Optional

from .rbase import check_target


def read_file(path: str, type_: Literal["str", "bytes"] = "bytes") -> Union[bytes, str]:
    """
    `Read` file data.

    Parameters
    ----------
    path : Read file path.
    type_ : File data type.
        - `Literal['bytes']` : Return file bytes data.
        - `Literal['str']` : Return file string data.

    Returns
    -------
    File bytes data or string data.
    """

    # Handle parameters.
    if type_ == "bytes":
        mode = "rb"
    elif type_ == "str":
        mode = "r"

    # Read.
    with open(path, mode) as file:
        content = file.read()

    return content


def write_file(path: str, content: Optional[Union[bytes, str]] = None, append: bool = False) -> None:
    """
    `Write` file data.

    Parameters
    ----------
    path : Write File path. When path not exist, then cerate file.
    content : Write data.
        - `bytes` : File bytes data.
        - `str` : File text.

    append : Whether append content, otherwise overwrite content.
    """

    # Get parameters.
    if append:
        mode = "a"
    else:
        mode = "w"
    if content.__class__ == bytes:
        mode += "b"

    # Write.
    with open(path, mode) as file:
        if content != None:
            file.write(content)