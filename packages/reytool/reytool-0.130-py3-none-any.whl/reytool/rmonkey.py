# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-03-19 19:36:47
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Monkey patch methods.
"""


def add_result_more_fetch() -> None:
    """
    Add more methods to CursorResult object of sqlalchemy package.
    """

    # Version compatible of package sqlalchemy.
    try:
        from sqlalchemy import CursorResult
    except ImportError:
        from sqlalchemy.engine.cursor import LegacyCursorResult as CursorResult

    from .rdata import to_table, to_df, to_json, to_sql, to_html, to_csv, to_excel


    # Fetch SQL result to table in List[Dict] format.
    CursorResult.fetch_table = to_table

    # Fetch SQL result to DataFrame object.
    CursorResult.fetch_df = to_df

    # Fetch SQL result to JSON string.
    CursorResult.fetch_json = to_json

    # Fetch SQL result to SQL string.
    CursorResult.fetch_sql = to_sql

    # Fetch SQL result to HTML string.
    CursorResult.fetch_sql = to_html

    # Fetch SQL result to save csv format file.
    CursorResult.fetch_csv = to_csv

    # Fetch SQL result to save excel file.
    CursorResult.fetch_excel = to_excel


def support_row_index_by_field():
    """
    Support Row object index by field name.
    """

    from typing import Any, Union, Sequence, overload
    from sqlalchemy.engine.row import Row


    # New method.
    @overload
    def __getitem__(self, index: Union[str, int, slice]) -> Union[Any, Sequence[Any]]: ...

    @overload
    def __getitem__(self, index: Union[str, int]) -> Any: ...

    @overload
    def __getitem__(self, index: slice) -> Sequence[Any]: ...

    def __getitem__(self, index: Union[str, int, slice]) -> Union[Any, Sequence[Any]]:
        """
        Index row value.

        Parameters
        ----------
        index : Field name or subscript or slice.

        Returns
        -------
        Index result.
        """

        # Index.
        if index.__class__ == str:
            value = self._mapping[index]
        else:
            value = self._data[index]

        return value


    # Modify index method.
    Row.__getitem__ = __getitem__


def modify_format_width_judgment() -> None:
    """
    Based on module pprint.pformat, modify the chinese width judgment.
    """

    from pprint import PrettyPrinter, _recursion
    from urwid import old_str_util


    # Chinese width can be determined.
    def get_width(text: str) -> int:
        """
        Get text display width.

        Parameters
        ----------
        text : Text.

        Returns
        -------
        Text display width.
        """

        # Get width.
        total_width = 0
        for char in text:
            char_unicode = ord(char)
            char_width = old_str_util.get_width(char_unicode)
            total_width += char_width

        return total_width


    # New method.
    def _format(_self, object, stream, indent, allowance, context, level):
        objid = id(object)
        if objid in context:
            stream.write(_recursion(object))
            _self._recursive = True
            _self._readable = False
            return
        rep = _self._repr(object, context, level)
        max_width = _self._width - indent - allowance
        width = get_width(rep)
        if width > max_width:
            p = _self._dispatch.get(type(object).__repr__, None)
            if p is not None:
                context[objid] = 1
                p(_self, object, stream, indent, allowance, context, level + 1)
                del context[objid]
                return
            elif isinstance(object, dict):
                context[objid] = 1
                _self._pprint_dict(object, stream, indent, allowance,
                                context, level + 1)
                del context[objid]
                return
        stream.write(rep)


    # Modify the chinese width judgment.
    PrettyPrinter._format = _format