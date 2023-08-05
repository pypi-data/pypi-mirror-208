# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:11:50
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Date time methods.
"""


from typing import Any, Dict, Literal, Optional, Union, overload
from pandas import DataFrame, concat as pd_concat
from time import time as time_time
from datetime import (
    datetime as datetime_datetime,
    date as datetime_date,
    time as datetime_time,
    timedelta as datetime_timedelta
)

from .rbase import check_target, is_number_str
from .rother import digits
from .rregular import re_search
from .rtext import rprint


@overload
def now(
    format: Literal["datetime", "date", "time", "timestamp", "datetime_str", "date_str", "time_str"] = "datetime_str"
) -> Union[datetime_datetime, datetime_date, datetime_time, int, str]: ...

@overload
def now(format: Literal["datatime"]) -> datetime_datetime: ...

@overload
def now(format: Literal["date"]) -> datetime_date: ...

@overload
def now(format: Literal["time"]) -> datetime_time: ...

@overload
def now(format: Literal["datetime_str", "date_str", "time_str"]) -> str: ...

@overload
def now(format: Literal["timestamp"]) -> int: ...

def now(
    format: Literal["datetime", "date", "time", "datetime_str", "date_str", "time_str", "timestamp"] = "datetime_str"
) -> Union[datetime_datetime, datetime_date, datetime_time, str, int]:
    """
    Get current time string or intger or object.

    Parameters
    ----------
    format : Format type.
        - Literal['datetime'] : Return datetime object of datetime package.
        - Literal['date'] : Return date object of datetime package.
        - Literal['time'] : Return time object of datetime package.
        - Literal['datetime_str'] : Return string in format '%Y-%m-%d %H:%M:%S'.
        - Literal['date_str'] : Return string in format '%Y-%m-%d'.
        - Literal['time_str'] : Return string in foramt '%H:%M:%S'.
        - Literal['timestamp'] : Return time stamp in milliseconds.

    Returns
    -------
    Time string or object of datetime package.
    """

    # Return time object by parameter format.
    if format == "datetime":
        return datetime_datetime.now()
    elif format == "date":
        return datetime_datetime.now().date()
    elif format == "time":
        return datetime_datetime.now().time()
    elif format == "datetime_str":
        return datetime_datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif format == "date_str":
        return datetime_datetime.now().strftime("%Y-%m-%d")
    elif format == "time_str":
        return datetime_datetime.now().strftime("%H:%M:%S")
    elif format == "timestamp":
        return int(time_time() * 1000)


@overload
def time2str(
    object_: Union[datetime_datetime, datetime_date, datetime_time, datetime_timedelta, int, Any],
    format: Optional[str] = None,
    throw_error: bool = False
) -> Union[str, Any]: ...

@overload
def time2str(object_: Union[datetime_datetime, datetime_date, datetime_time, datetime_timedelta, int]) -> str: ...

@overload
def time2str(object_: Any) -> Any: ...

def time2str(
    object_: Union[datetime_datetime, datetime_date, datetime_time, datetime_timedelta, int, Any],
    format: Optional[str] = None,
    throw_error: bool = False
) -> Union[str, Any]:
    """
    Format time object of 'datetime' package to string

    Parameters
    ----------
    object_ : Object of 'datetime' package or int.
    format : Format string.
        - None : Automatic by type.
            * Parameter 'object_' is datetime_datetime : Is '%Y-%m-%d %H:%M:%S'.
            * Parameter 'object_' is datetime_date : Is '%Y-%m-%d'.
            * Parameter 'object_' is datetime_time : Is '%H:%M:%S'.
            * Parameter 'object_' is datetime_timedelta : Is f'{days} %H:%M:%S'.
            * Parameter 'object_' is time stamp : Is '%Y-%m-%d %H:%M:%S'.
        - str : Format by this value.

    throw_error : Whether throw error, when parameter 'object_' value error, otherwise return original value.

    Returns
    -------
    String after foramt or original value.
    """

    # Check parameters.
    if throw_error:
        check_target(object_, datetime_datetime, datetime_date, datetime_time, datetime_timedelta, int)

    # Convert to time string.

    ## From datetime object.
    if object_.__class__ == datetime_datetime:
        if format == None:
            string = str(object_)[:19]
        else:
            string = object_.strftime(format)

    ## From date object.
    elif object_.__class__ == datetime_date:
        if format == None:
            string = str(object_)[:10]
        else:
            string = object_.strftime(format)

    ## From time object.
    elif object_.__class__ == datetime_time:
        if format == None:
            string = str(object_)[:8]
        else:
            string = object_.strftime(format)

    ## From timedelta object.
    elif object_.__class__ == datetime_timedelta:
        if format == None:
            string = str(object_)
            if "day" in string:
                day, char, string = string.split(" ")
            else:
                day = "0"
            if string[1] == ":":
                string = "0" + string
            string = "%s %s" % (day, string[:8])
        else:
            seconds = object_.microseconds / 1000_000
            datetime_obj = datetime_datetime.fromtimestamp(seconds)
            string = datetime_obj.strftime(format)

    ## From int object.
    elif object_.__class__ == int:
        int_len = len(str(object_))
        if int_len > 10:
            divisor = 10 ** (int_len - 10)
            seconds = object_ / divisor
        else:
            seconds = object_
        datetime_obj = datetime_datetime.fromtimestamp(seconds)
        if format == None:
            format = "%Y-%m-%d %H:%M:%S"
        string = datetime_obj.strftime(format)

    ## From other object.
    else:
        return object_

    return string


@overload
def str2time(
    string: Union[str, Any],
    type_: Optional[Literal["datetime", "date", "time", "timedelta", "timestamp"]] = None,
    format: Optional[str] = None,
    throw_error: bool = False
) -> Union[datetime_datetime, datetime_date, datetime_time, datetime_timedelta, int, Any]: ...

@overload
def str2time(type_: Literal["datetime"]) -> Union[datetime_datetime, Any]: ...

@overload
def str2time(type_: Literal["date"]) -> Union[datetime_date, Any]: ...

@overload
def str2time(type_: Literal["time"]) -> Union[datetime_time, Any]: ...

@overload
def str2time(type_: Literal["timedelta"]) -> Union[datetime_timedelta, Any]: ...

@overload
def str2time(type_: Literal["timestamp"]) -> Union[int, Any]: ...

@overload
def str2time(type_: None) -> Union[datetime_datetime, datetime_date, datetime_time, datetime_timedelta, Any]: ...

def str2time(
    string: Union[str, Any],
    type_: Optional[Literal["datetime", "date", "time", "timedelta", "timestamp"]] = None,
    format: Optional[str] = None,
    throw_error: bool = False
) -> Union[datetime_datetime, datetime_date, datetime_time, datetime_timedelta, int, Any]:
    """
    Format string to time object of datetime package

    Parameters
    ----------
    string : Time string.
    type_ : Format type.
        - None : Automatic judgment.
        - Literal['datetime'] : Return datetime object of datetime package.
        - Literal['date'] : Return date object of datetime package.
        - Literal['time'] : Return time object of datetime package.
        - Literal['timedelta'] : Return timedelta object of datetime package.
        - Literal['timestamp'] : Return time stamp in milliseconds.

    format : Format string.
        - None : Default format method.
            * Parameter 'type_' is 'datetime' : Is '%Y-%m-%d %H:%M:%S'.
            * Parameter 'type_' is 'date' : Is '%Y-%m-%d'.
            * Parameter 'type_' is 'time' : Is '%H:%M:%S'.
            * Parameter 'type_' is 'timedelta' : Is 'days %H:%M:%S'.
            * Parameter 'type_' is 'timestamp' : Is '%Y-%m-%d %H:%M:%S'.
            * Parameter 'type_' is None : automatic judgment.
        - str : Format by this value.

    throw_error : Whether throw error, when parameter 'time_obj' value error, otherwise return original value.

    Returns
    -------
    Time object of datetime package or time stamp or original value.
    """

    # Check parameters.
    if string.__class__ != str:
        return string

    # Get time format by automatic judgment.
    if type_ == None:
        str_len = len(string)
        if "年" == string[4:5]:
            if str_len > 11:
                format = "%Y年%m月%d日 %H时%M分%S秒"
                type_ = "datetime"
            else:
                format = "%Y年%m月%d日"
                type_ = "date"
        elif "时" in string[1:3]:
            format = "%H时%M分%S秒"
            type_ = "time"
        elif " " in string and "-" not in string:
            format = "%H:%M:%S"
            type_ = "timedelta"
        elif str_len == 19:
            format = "%Y-%m-%d %H:%M:%S"
            type_ = "datetime"
        elif str_len == 14:
            format = "%Y%m%d%H%M%S"
            type_ = "datetime"
        elif str_len == 10:
            format = "%Y-%m-%d"
            type_ = "date"
        elif str_len == 8:
            if string[2] == ":":
                format = "%H:%M:%S"
                type_ = "time"
            else:
                format = "%Y%m%d"
                type_ = "date"
        elif str_len == 6:
            format = "%H%M%S"
            type_ = "time"
        elif str_len == 4:
            format = "%Y"
            type_ = "date"
        else:
            return string

    # Get time format by parameter 'type_'.
    else:
        if format == None:
            format_dir = {
                "datetime": "%Y-%m-%d %H:%M:%S",
                "date": "%Y-%m-%d",
                "time": "%H:%M:%S",
                "timestamp": "%Y-%m-%d %H:%M:%S",
                "timedelta": "%H:%M:%S"
            }
            format = format_dir[type_]

    # Additional processing timedelta type.
    if type_ == "timedelta":
        if " " in string:
            strings = string.split(" ")
            day_str, string = strings[0], strings[-1]
        else:
            day = "0"
        try:
            day = int(day_str)
        except ValueError:
            if throw_error:
                raise ValueError("failed to format string as time object")
            return string

    # Convert to time type.
    try:
        time_obj = datetime_datetime.strptime(string, format)
    except ValueError:
        if throw_error:
            raise ValueError("failed to format string as time object")
        return string
    if type_ == "date":
        time_obj = time_obj.date()
    elif type_ == "time":
        time_obj = time_obj.time()
    elif type_ == "timestamp":
        time_obj = int(time_obj.timestamp() * 1000)
    elif type_ == "timedelta":
        second = time_obj.second
        second += day * 86400
        time_obj = datetime_timedelta(seconds=second)

    return time_obj


@overload
def is_sql_time(content: Union[str, int], return_datatime: bool = False) -> Union[bool, datetime_datetime]: ...

@overload
def is_sql_time(return_datatime: Literal[False]) -> bool: ...

@overload
def is_sql_time(return_datatime: Literal[True]) -> datetime_datetime: ...

def is_sql_time(
    content: Union[str, int],
    return_datatime: bool = False
) -> Union[bool, datetime_datetime]:
    """
    Judge whether it conforms to SQL time format.

    Parameters
    ----------
    content : Judge object.
    return_datatime : Whether return datetime object.

    Returns
    -------
    Judgment result or transformed values.
    """

    # Extract number string.

    ## From str object.
    if content.__class__ == str:
        content_len = len(content)
        if content_len < 5:
            return False
        if is_number_str(content[4]):
            if content_len == 8:
                datetimes_str = [content[0:4], content[4:6], content[6:8], None, None, None]
            else:
                pattern = "^(\d{2}|\d{4})(\d{2})(\d{1,2})(\d{0,2})(\d{0,2})(\d{0,2})$"
                result = re_search(pattern, content)
                datetimes_str = list(result)
        else:
            pattern = "^(\d{2}|\d{4})[\W_](\d{2})[\W_](\d{2})[\W_]?(\d{2})?[\W_]?(\d{2})?[\W_]?(\d{2})?$"
            result = re_search(pattern, content)
            datetimes_str = list(result)

    ## From int object.
    elif content.__class__ == int:
        content = str(content)
        content_len = len(content)
        if content_len < 3:
            return False
        elif content_len <= 8:
            pattern = r"^(\d{0,4}?)(\d{1,2}?)(\d{2})$"
            result = re_search(pattern, content)
            datetimes_str = list(result)
            datetimes_str += [None, None, None]
        else:
            pattern = r"^(\d{0,4}?)(\d{1,2})(\d{2})(\d{2})(\d{2})(\d{2})$"
            result = re_search(pattern, content)
            datetimes_str = list(result)

    # Judge.
    year_len = len(datetimes_str[0])
    datetimes_str[0] = "2000"[0:4-year_len] + datetimes_str[0]
    year, month, day, hour, minute, second = [
        0 if int_str in ("", None) else int(int_str)
        for int_str in datetimes_str
    ]
    try:
        datetime_datetime(year, month, day, hour, minute, second)
    except ValueError:
        return False

    # Return datatime object.
    if return_datatime:
        return datetime_datetime(year, month, day, hour, minute, second)

    return True


class RDateTimeMark():
    """
    Rey's date time mark type.
    """


    def __init__(self) -> None:
        """
        Mark now time.
        """

        # Marking.
        self.mark()


    def mark(self) -> Dict[
        Literal["index", "timestamp", "datetime", "datetime_str", "interval_timestamp", "interval_timedelta", "interval_timedelta_str"],
        Optional[Union[str, float, datetime_datetime, datetime_timedelta]]
    ]:
        """
        Mark now time and return mark time information.

        Returns
        -------
        Mark time information.
        """

        # Compatible with first marking.
        if "record" not in self.__dir__():
            self.record = []

        # Get parametes.
        record_len = len(self.record)
        mark_info = {
            "index": record_len,
            "timestamp": now("timestamp"),
            "datetime": now("datetime"),
            "datetime_str": now(),
        }

        # Marking.

        ## First.
        if record_len == 0:
            mark_info["interval_timestamp"] = None
            mark_info["interval_timedelta"] = None
            mark_info["interval_timedelta_str"] = None

        ## Non first.
        else:
            last_datetime = self.record[-1]["datetime"]
            last_timestamp = self.record[-1]["timestamp"]
            mark_info["interval_timestamp"] = mark_info["timestamp"] - last_timestamp
            mark_info["interval_timedelta"] = mark_info["datetime"] - last_datetime
            mark_info["interval_timedelta_str"] = time2str(mark_info["interval_timedelta"])

        self.record.append(mark_info)

        return mark_info


    def report(self) -> DataFrame:
        """
        Print and return mark time information.

        Returns
        -------
        DataFrame object of pandas package with mark time information.
        """

        # Get parameters.
        data = [
            {
                "timestamp": row["timestamp"],
                "datetime": row["datetime_str"],
                "interval": row["interval_timedelta_str"]
            }
            for row in self.record
        ]

        # Generate report.
        report_df = DataFrame(data)
        interval_timedelta = self.record[-1]["datetime"] - self.record[0]["datetime"]
        interval = time2str(interval_timedelta)
        sum_df = DataFrame({"interval": interval}, index = ["sum"])
        report_df = pd_concat([report_df, sum_df])
        report_df.fillna("-", inplace=True)

        # Report.
        title = "Time Mark"
        rprint(report_df, title=title)

        return report_df