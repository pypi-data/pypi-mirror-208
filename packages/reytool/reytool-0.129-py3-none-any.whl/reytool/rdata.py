# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:10:42
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Data methods.
"""


from typing import Any, List, Dict, Iterable, Literal, Optional, Union, Type, NoReturn, overload
from pandas import DataFrame, ExcelWriter
from os.path import abspath as os_path_abspath

# Version compatible of package sqlalchemy.
try:
    from sqlalchemy import CursorResult
except ImportError:
    from sqlalchemy.engine.cursor import LegacyCursorResult as CursorResult

from .rbase import is_iterable, check_least_one, check_most_one, to_type
from .rdatetime import time2str


def to_table(
    data: Union[CursorResult, DataFrame, List[Dict], Iterable[Iterable]],
    fields: Optional[Iterable] = None
) -> List[Dict]:
    """
    Fetch data to table in List[Dict] format, keys and keys sort of the dictionary are the same.

    Parameters
    ----------
    data : Data.
    fields : Table fields.
        - None : Infer.
        - Iterable : Use values in Iterable.

    Returns
    -------
    Table in List[Dict] format.
    """

    # Convert.

    ## From CursorResult object.
    if data.__class__ == CursorResult:
        if fields == None:
            fields = data.keys()
        data_table = [
            dict(zip(fields, row))
            for row in data
        ]

    ## From DataFrame object.
    elif data.__class__ == DataFrame:
        data_df = data.copy()
        if fields != None:
            data_df.columns = fields
        data_df = data_df.where(data.notnull(), None)
        data_table = data_df.to_dict("records")

    ## From other object.
    else:
        data_df = DataFrame(data, columns=fields)
        data_df = data_df.where(data.notnull(), None)
        data_table = data_df.to_dict("records")

    return data_table


def to_df(data: Union[CursorResult, DataFrame, List[Dict], Iterable[Iterable]], fields: Optional[Iterable] = None) -> DataFrame:
    """
    Fetch data to table of DataFrame object.

    Parameters
    ----------
    data : Data.
    fields : Table fields.
        - None : Infer.
        - Iterable : Use values in Iterable.

    Returns
    -------
    DataFrame object.
    """

    # Convert.

    ## From CursorResult object.
    if data.__class__ == CursorResult:
        if fields == None:
            fields = data.keys()
        data_df = DataFrame(data, columns=fields)

    ## From DataFrame object.
    elif data.__class__ == DataFrame:
        data_df = data.copy()
        if fields != None:
            data_df.columns = fields
        return data_df

    ## From other object.
    else:
        data_df = DataFrame(data, columns=fields)

    return data_df


def to_json(data: Union[CursorResult, DataFrame, List[Dict], Iterable[Iterable]], fields: Optional[Iterable] = None) -> str:
    """
    Fetch data to JSON string.

    Parameters
    ----------
    data : Data.
    fields : Table fields.
        - None : Infer.
        - Iterable : Use values in Iterable.

    Returns
    -------
    JSON string.
    """

    # Handle parameters.
    data_df = to_df(data, fields)

    # Convert.
    data_json = data_df.to_json(orient="records", force_ascii=False)

    return data_json


def to_sql(data: Union[CursorResult, DataFrame, List[Dict], Iterable[Iterable]], fields: Optional[Iterable] = None) -> str:
    """
    Fetch data to SQL string.

    Parameters
    ----------
    data : Data.
    fields : Table fields.
        - None : Infer.
        - Iterable : Use values in Iterable.

    Returns
    -------
    SQL string.
    """

    # Get fields of table.
    if data.__class__ == CursorResult:
        if fields == None:
            fields = data.keys()
    else:
        data = to_table(data, fields)
        fields = data[0].keys()

    # Generate SQL.
    sql_rows_values = [
        [
            repr(time2str(val, "%Y-%m-%d %H:%M:%S"))
            if val != None
            else "NULL"
            for val in row
        ]
        for row in data
    ]
    sql_rows = [
        "SELECT " + ",".join(row_values)
        for row_values in sql_rows_values
    ]
    sql_row_first = "SELECT " + ",".join(
        [
            "%s AS `%s`" % (val, key)
            for key, val in list(zip(fields, sql_rows_values[0]))
        ]
    )
    sql_rows[0] = sql_row_first
    data_sql = " UNION ALL ".join(sql_rows)

    return data_sql


def to_html(data: Union[CursorResult, DataFrame, List[Dict], Iterable[Iterable]], fields: Optional[Iterable] = None) -> str:
    """
    Fetch data to HTML string.

    Parameters
    ----------
    data : Data.
    fields : Table fields.
        - None : Infer.
        - Iterable : Use values in Iterable.

    Returns
    -------
    HTML string.
    """

    # Handle parameters.
    data_df = to_df(data, fields)

    # Convert.
    data_html = data_df.to_html(col_space=50, index=False, justify="center")

    return data_html


def to_csv(
    data: Union[CursorResult, DataFrame, Iterable[Dict], Iterable],
    path: str = "data.csv",
    fields: Optional[Iterable] = None
) -> str:
    """
    Fetch data to save csv format file.

    Parameters
    ----------
    data : Data.
    path : File save path.
    fields : Table fields.
        - None : Infer.
        - Iterable : Use values in Iterable.

    Returns
    -------
    File absolute path.
    """

    # Handle parameters.
    data_df = to_df(data, fields)
    path = os_path_abspath(path)

    # Save file.
    data_df.to_csv(path, mode="a")

    return path


def to_excel(
    data: Union[CursorResult, DataFrame, Iterable[Dict], Iterable],
    path: str = "data.xlsx",
    group_field: Optional[str] = None,
    sheets_set: Dict[Union[str, int], Dict[Literal["name", "index", "filter"], Union[str, int, List[str]]]] = {}
) -> str:
    """
    Fetch data to save excel format file and return sheet name and sheet data.

    Parameters
    ----------
    data : Data.
    path : File save path.
    group_field : Group filed.
    sheets_set : Set sheet new name and sort sheet and filter sheet fields,
        key is old name or index, value is set parameters.
        - Parameter 'name' : Set sheet new name.
        - Parameter 'index' : Sort sheet.
        - Parameter 'filter' : Filter sheet fields.

    Returns
    -------
    File absolute path.
    """

    # Handle parameters.
    if data.__class__ != DataFrame:
        data = to_df(data)
    path = os_path_abspath(path)

    # Generate sheets.
    if group_field == None:
        data_group = (("Sheet1", data),)
    else:
        data_group = data.groupby(group_field)
    sheets_table_before = []
    sheets_table_after = []
    for index, sheet_table in enumerate(data_group):
        sheet_name, sheet_df = sheet_table
        if group_field != None:
                del sheet_df[group_field]
        if sheet_name in sheets_set:
            sheet_set = sheets_set[sheet_name]
        elif index in sheets_set:
            sheet_set = sheets_set[index]
        else:
            sheets_table_after.append((sheet_name, sheet_df))
            continue
        if "name" in sheet_set:
            sheet_name = sheet_set["name"]
        if "filter" in sheet_set:
            sheet_df = sheet_df[sheet_set["filter"]]
        if "index" in sheet_set:
            sheets_table_before.append((sheet_set["index"], (sheet_name, sheet_df)))
        else:
            sheets_table_after.append((sheet_name, sheet_df))
    sort_func = lambda item: item[0]
    sheets_table_before.sort(key=sort_func)
    sheets_table = [sheet_table for sheet_index, sheet_table in sheets_table_before] + sheets_table_after

    # Save file.
    excel = ExcelWriter(path)
    for sheet_name, sheet_df in sheets_table:
        sheet_df.to_excel(excel, sheet_name, index=False)
    excel.close()

    return path


def count(
    data: Any,
    count_value: Dict = {"size": 0, "total": 0, "types": {}},
    _surface: bool = True
) -> Dict[Literal["size", "total", "types"], Union[int, Dict[Type, int]]]:
    """
    Count data element.

    Parameters
    ----------
    data : Data.
    count_value : Cumulative Count.
    _surface : Whether is surface recursion.

    Returns
    -------
    Count data.
    """

    # Count Element.
    count_value["total"] += 1
    count_value["types"][data.__class__] = count_value["types"].get(data.__class__, 0) + 1

    # Recursion.
    if data.__class__ == dict:
        for element in data.values():
            count(element, count_value, False)
    elif is_iterable(data):
        for element in data:
            count(element, count_value, False)
    else:
        count_value["size"] = count_value["size"] + 1

    # End Recursion and return.
    if _surface:

        ## Sort by count.
        sorted_func = lambda key: count_value["types"][key]
        sorted_key = sorted(count_value["types"], key=sorted_func, reverse=True)
        count_value["types"] = {key: count_value["types"][key] for key in sorted_key}

        return count_value


def flatten(data: Any, flattern_data: List = []) -> List:
    """
    Flatten data.

    Parameters
    ----------
    data : Data.
    flattern_data : Recursion cumulative data.

    Returns
    -------
    Data after flatten.
    """

    # Flatten.

    ## Recursion dict object.
    if data.__class__ == dict:
        for element in data.values():
            _ = flatten(element, flattern_data)

    ## Recursion iterator.
    elif is_iterable(data):
        for element in data:
            _ = flatten(element, flattern_data)

    ## Other.
    else:
        flattern_data.append(data)

    return flattern_data


@overload
def split(data: Iterable, share: Optional[int] = None, bin_size: Optional[int] = None) -> List[List]: ...

@overload
def split(share: None, bin_size: None) -> NoReturn: ...

@overload
def split(share: int, bin_size: int) -> NoReturn: ...

def split(data: Iterable, share: Optional[int] = None, bin_size: Optional[int] = None) -> List[List]:
    """
    Split data into multiple data.

    Parameters
    ----------
    data : Data.
    share : Number of splie share.
    bin_size : Size of each bin.

    Returns
    -------
    Split data.
    """

    # Check parameters.
    check_least_one(share, bin_size)
    check_most_one(share, bin_size)

    # Handle parameters.
    data = list(data)

    # Split.
    data_len = len(data)
    _data = []
    _data_len = 0

    ## by number of share.
    if share != None:
        average = data_len / share
        for n in range(share):
            bin_size = int(average * (n + 1)) - int(average * n)
            _data = data[_data_len:_data_len + bin_size]
            _data.append(_data)
            _data_len += bin_size

    ## By size of bin.
    elif bin_size != None:
        while True:
            _data = data[_data_len:_data_len + bin_size]
            _data.append(_data)
            _data_len += bin_size
            if _data_len > data_len:
                break

    return _data


def unique(data: Iterable) -> List:
    """
    De duplication of data.

    Parameters
    ----------
    data : Data.

    Returns
    -------
    List after de duplication.
    """

    # Handle parameters.
    data = to_type(data, tuple)

    # Delete duplicate.
    data_unique = list(set(data))
    data_unique.sort(key=data.index)
    return data_unique


def ins(obj: Any, *arrays: Iterable) -> bool:
    """
    Judge whether the object is in multiple array.

    Parameters
    ----------
    obj : Judge object.
    arrays : Array.

    Returns
    -------
    Judge result.
    """

    # Judge.
    for array in arrays:
        if obj in array:
            return True

    return False


def mutual_in(*arrays: Iterable) -> bool:
    """
    Whether the same element exists in multiple array.

    Parameters
    ----------
    arrays : Array.

    Returns
    -------
    Judge result.
    """

    # Handle parameters.
    arrays = list(arrays)

    # Judge.
    for n, array in enumerate(arrays):
        for after_array in arrays[n+1:]:
            for element in array:
                if ins(element, after_array):
                    return True

    return False