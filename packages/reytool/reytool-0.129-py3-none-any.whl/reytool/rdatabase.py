# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:10:02
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Database methods.
"""


from typing import Any, List, Tuple, Dict, Iterable, Optional, Literal, Union, ClassVar, NoReturn, overload
from re import findall
from sqlalchemy import create_engine as sqlalchemy_create_engine, text
from sqlalchemy.engine.base import Engine, Connection, RootTransaction
from sqlalchemy.engine.url import URL
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.exc import OperationalError

from .rbase import exc, get_first_notnull
from .rdata import to_table
from .rmonkey import add_result_more_fetch, support_row_index_by_field
from .rregular import re_search
from .rtext import rprint
from .rwrap import runtime, retry

# Version compatible of package sqlalchemy.
try:
    from sqlalchemy import CursorResult
except ImportError:
    from sqlalchemy.engine.cursor import LegacyCursorResult as CursorResult


# Add more methods to CursorResult object of sqlalchemy package.
add_result_more_fetch()

# Support Row object index by field name.
support_row_index_by_field()


class REngine(object):
    """
    Rey's database Engine type, based on the package sqlalchemy.
    """

    # Values to be converted to "NULL".
    null_values: ClassVar[List] = ["", " ", b"", [], (), {}, set()]


    @overload
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        drivername: Optional[str] = None,
        url: Optional[Union[str, URL]] = None,
        engine: Optional[Union[Engine, Connection]] = None,
        recycle: int = 28800,
        **query: str
    ) -> None: ...

    @overload
    def __init__(self, username: None, url: None, engine: None) -> NoReturn: ...

    @overload
    def __init__(self, password: None, url: None, engine: None) -> NoReturn: ...

    @overload
    def __init__(self, host: None, url: None, engine: None) -> NoReturn: ...

    @overload
    def __init__(self, port: None, url: None, engine: None) -> NoReturn: ...

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        drivername: Optional[str] = None,
        url: Optional[Union[str, URL]] = None,
        engine: Optional[Union[Engine, Connection]] = None,
        recycle: int = -1,
        **query: str
    ) -> None:
        """
        Create database Engine object and set parameters.

        Parameters
        ----------
        username : Server user name.
        password : Server password.
        host : Server host.
        port : Server port.
        database : Database name in the server.
        drivername : Database backend and driver name.
        url: Server server URL, will get parameters from it, but preferred input parameters.
        engine : Using existing Engine or Connection object.
        recycle : Connection object recycling seconds.
            - Literal[-1] : No recycling.
            - int : Use this recycling seconds.

        query : Server parameters.
        """

        # From existing Engine object.
        if engine != None:

            ## Extract Engine object from Connection boject.
            if engine.__class__ == Connection:
                engine = engine.engine

            ## Extract parameters and save.
            self.drivername = engine.url.drivername
            self.username = engine.url.username
            self.password = engine.url.password
            self.host = engine.url.host
            self.port = engine.url.port
            self.database = engine.url.database
            self.query = dict(engine.url.query)
            self.recycle = engine.pool._recycle

            ## Save Engine object.
            self.engine = engine

        # From parameters create.
        else:

            ## Extract parameters from URL of str object.
            if url.__class__ == str:
                pattern = "^([\w\+]+)://(\w+):(\w+)@(\d+\.\d+\.\d+\.\d+):(\d+)[/]?([\w/]+)?[\?]?([\w&=]+)?$"
                url_params = re_search(pattern, url)
                if url_params == None:
                    raise ValueError("the value of parameter 'url' is incorrect")
                url_drivername, url_username, url_password, url_host, url_port, url_database, url_query_str = url_params
                if url_query_str != None:
                    pattern = "(\w+)=(\w+)"
                    url_query_findall = findall(pattern, url_query_str)
                    url_query = {key: val for key, val in url_query_findall}
                else:
                    url_query = {}

            ## Extract parameters from URL of URL object.
            elif url.__class__ == URL:
                url_drivername = url.drivername
                url_username = url.username
                url_password = url.password
                url_host = url.host
                url_port = url.port
                url_database = url.database
                url_query = dict(url.query)

            else:
                url_drivername, url_username, url_password, url_host, url_port, url_database, url_query = (
                    None, None, None, None, None, None, {}
                )

            ## Set parameters by priority.
            self.drivername = get_first_notnull(drivername, url_drivername)
            self.username = get_first_notnull(username, url_username, default="error")
            self.password = get_first_notnull(password, url_password, default="error")
            self.host = get_first_notnull(host, url_host, default="error")
            self.port = get_first_notnull(port, url_port, default="error")
            self.database = get_first_notnull(database, url_database)
            self.query = get_first_notnull(query, url_query, default={"charset": "utf8"}, null_values=[{}])
            self.recycle = recycle

            ## Create Engine object.
            self.engine = self.create_engine()


    def url(self) -> str:
        """
        Generate server URL.

        Returns
        -------
        Server URL.
        """

        # Generate URL.
        _url = f"{self.drivername}://{self.username}:{self.password}@{self.host}:{self.port}"

        # Add database path.
        if self.database != None:
            _url = f"{_url}/{self.database}"

        # Add Server parameters.
        if self.query != {}:
            query = "&".join(
                [
                    "%s=%s" % (key, val)
                    for key, val in self.query.items()
                ]
            )
            _url = f"{_url}?{query}"

        return _url


    def create_engine(self) -> Engine:
        """
        Create database Engine object.

        Returns
        -------
        Engine object.
        """

        # Handle parameters.
        if self.drivername == None:
            drivernames = ("mysql+mysqldb", "mysql+pymysql")
        else:
            drivernames = (self.drivername,)

        # Create Engine object.
        for drivername in drivernames:
            self.drivername = drivername
            url = self.url()
            try:
                engine = sqlalchemy_create_engine(url, pool_recycle=self.recycle)
                return engine
            except ModuleNotFoundError:
                pass

        # Throw error.
        drivernames_str = " and ".join(
            [
                dirvername.split("+", 1)[-1]
                for dirvername in drivernames
            ]
        )
        raise ModuleNotFoundError("module %s not fund" % drivernames_str)


    def fill_data(
        self,
        data: Union[Dict, List[Dict]],
        sql: Union[str, TextClause],
    ) -> List[Dict]:
        """
        Fill missing data according to contents of sqlClause object of sqlalchemy module, and filter out empty Dict.

        Parameters
        ----------
        data : Data set for filling.
        sql : SQL in method sqlalchemy.text format, or TextClause object.

        Returns
        -------
        Filled data.
        """

        # Handle parameters.
        if data.__class__ == dict:
            data = [data]
        if sql.__class__ == TextClause:
            sql = sql.text

        # Filter out empty Dict.
        data = [
            param
            for param in data
            if param != {}
        ]

        # Extract fill field names.
        pattern = "(?<!\\\):(\w+)"
        sql_keys = findall(pattern, sql)

        # Fill data.
        for param in data:
            for key in sql_keys:
                val = param.get(key)
                if val in self.null_values:
                    val = None
                param[key] = val

        return data


    def get_syntax(self, sql: Union[str, TextClause]) -> str:
        """
        Extract syntax type form SQL.

        Parameters
        ----------
        sql : SQL text or TextClause object.

        Returns
        -------
        SQL syntax type.
        """

        # Handle parameters.
        if sql.__class__ == TextClause:
            sql = sql.text

        # Extract.
        split_sql = sql.split(maxsplit=1)
        syntax_type = split_sql[0]
        syntax_type = syntax_type.upper()

        return syntax_type


    def execute_report(
        self,
        connection: Connection,
        sql: TextClause,
        data: List[Dict]
    ) -> CursorResult:
        """
        Execute SQL and report result.

        Parameters
        ----------
        connection : Connection object.
        sql : TextClause object.
        data : Data set for filling.

        Returns
        -------
        CursorResult object of alsqlchemy package.
        """

        # Decorate and execute.
        result, report_runtime = runtime(connection.execute, sql, data, _return_report=True)

        # Report.
        report_info = "%s\nRow Count: %d" % (report_runtime, result.rowcount)
        if data == []:
            rprint(report_info, sql, title="SQL")
        else:
            rprint(report_info, sql, data, title="SQL")

        return result


    def executor(
        self,
        sql: Union[str, TextClause],
        data: Optional[Union[List[Dict], Dict]] = None,
        report: bool = False
    ) -> CursorResult:
        """
        SQL executor.

        Parameters
        ----------
        sql : SQL in method sqlalchemy.text format, or TextClause object.
        data : Data set for filling.
        report : Whether print SQL and execute run time.

        Returns
        -------
        CursorResult object of alsqlchemy package.
        """

        # When REngine.
        if self.__class__ == REngine:

            ## Create Connection object.
            with self.engine.connect() as connection:

                ## Create Transaction object.
                with connection.begin():

                    ## Execute.
                    if report:
                        result = self.execute_report(connection, sql, data)
                    else:
                        result = connection.execute(sql, data)

        # When RConnection.
        elif self.__class__ == RConnection:

            ## Create Transaction object.
            if self.begin_count == 0:
                if self.begin != None:
                    self.begin.close()
                self.begin = self.connection.begin()

            ## Execute.
            if report:
                result = self.execute_report(self.connection, sql, data)
            else:
                result = self.connection.execute(sql, data)

            ## Execute Count.
            syntax = self.get_syntax(sql)
            if syntax in ("UPDATE", "INSERT", "DELETE"):
                self.begin_count += 1

        return result


    def execute(
        self,
        sql: Union[str, TextClause],
        data: Optional[Union[List[Dict], Dict]] = None,
        report: bool = False,
        **kwdata: Any
    ) -> CursorResult:
        """
        Execute SQL.

        Parameters
        ----------
        sql : SQL in method sqlalchemy.text format, or TextClause object.
        data : Data set for filling.
        report : Whether print SQL and execute run time.
        kwdata : Keyword data for filling sqlalchemy.text.

        Returns
        -------
        CursorResult object of alsqlchemy package.
        """

        # Handle parameters.
        if sql.__class__ == str:
            sql = text(sql)
        if data != None:
            if data.__class__ == dict:
                data = [data]
            else:
                data = data.copy()
            for param in data:
                param.update(kwdata)
        else:
            data = [kwdata]
        data = self.fill_data(data, sql)

        # Execute.

        ## When REngine.
        if self.__class__ == REngine:

            ### Can retry.
            result = retry(
                self.executor,
                sql,
                data,
                report,
                _report="Database execute operational error",
                _exception=OperationalError
            )

        ## When RConnection.
        elif self.__class__ == RConnection:

            ### Can retry when not counted.
            if self.begin_count == 0:
                result = retry(
                self.executor,
                sql,
                data,
                report,
                _report="Database execute operational error",
                _exception=OperationalError
            )

            ### Cannot retry when counted.
            else:
                result = self.executor(sql, data, report)

        return result


    def execute_select(
            self,
            table: str,
            database: Optional[str] = None,
            fields: Optional[Union[str, Iterable]] = None,
            where: Optional[str] = None,
            group: Optional[str] = None,
            having: Optional[str] = None,
            order: Optional[str] = None,
            limit: Optional[Union[int, str, List, Tuple]] = None,
            report: bool = False
        ) -> CursorResult:
        """
        Execute select SQL.

        Parameters
        ----------
        table : Table name.
        database : Database name.
        fields : Select clause content.
            - None : Is 'SELECT *'.
            - str : Join as 'SELECT str'.
            - Iterable[str] : Join as 'SELECT \`str\`, ...'.

        where : 'WHERE' clause content, join as 'WHERE str'.
        group : 'GROUP BY' clause content, join as 'GROUP BY str'.
        having : 'HAVING' clause content, join as 'HAVING str'.
        order : 'ORDER BY' clause content, join as 'ORDER BY str'.
        limit : 'LIMIT' clause content.
            - Union[int, str] : Join as 'LIMIT int/str'.
            - Union[List, Tuple] with length of 1 or 2 'int/str' : Join as 'LIMIT int/str [, int/str]'.

        report : Whether print SQL and execute run time.

        Returns
        -------
        CursorResult object of alsqlchemy package.
        """

        # Handle parameters.
        if database == None:
            _database = self.database
        else:
            _database = database

        # Generate SQL.
        sqls = []

        ## Part 'SELECT' syntax.
        if fields == None:
            fields = "*"
        elif fields.__class__ != str:
            fields = ",".join(["`%s`" % field for field in fields])
        sql_select = f"SELECT {fields}"
        sqls.append(sql_select)

        ## Part 'FROM' syntax.
        sql_from =  f"FROM `{_database}`.`{table}`"
        sqls.append(sql_from)

        ## Part 'WHERE' syntax.
        if where != None:
            sql_where = "WHERE %s" % where
            sqls.append(sql_where)

        ## Part 'GROUP BY' syntax.
        if group != None:
            sql_group = "GROUP BY %s" % group
            sqls.append(sql_group)

        ## Part 'GROUP BY' syntax.
        if having != None:
            sql_having = "HAVING %s" % having
            sqls.append(sql_having)

        ## Part 'ORDER BY' syntax.
        if order != None:
            sql_order = "ORDER BY %s" % order
            sqls.append(sql_order)

        ## Part 'LIMIT' syntax.
        if limit != None:
            if limit.__class__ in (str, int):
                sql_limit = f"LIMIT {limit}"
            else:
                if len(limit) in (1, 2):
                    limit_content = ",".join([str(val) for val in limit])
                    sql_limit = "LIMIT %s" % limit_content
                else:
                    raise ValueError("The length of the parameter 'limit' value must be 1 or 2")
            sqls.append(sql_limit)

        sql = "\n".join(sqls)

        # Execute SQL.
        result = self.execute(sql, report=report)

        return result


    def execute_update(
        self,
        data: Union[CursorResult, List[Dict], Dict],
        table: str,
        database: Optional[str] = None,
        where_fields: Optional[Union[str, Iterable[str]]] = None,
        report: bool = False
    ) -> Optional[CursorResult]:
        """
        Update the data of table in the datebase.

        Parameters
        ----------
        data : Updated data.
        table : Table name.
        database : Database name.
        where_fields : 'WHERE' clause content.
            - None : The first key value pair of each item is judged.
            - str : This key value pair of each item is judged.
            - Iterable[str] : Multiple judged, 'and' relationship.

        report : Whether print SQL and execute run time.

        Returns
        -------
        None or CursorResult object.
            - None : When the data is empty.
            - CursorResult object : When the data is not empty.
        """

        # Handle parameters.
        if data.__class__ == CursorResult:
            data = to_table(data)
        elif data.__class__ == dict:
            data = [data]
        if database == None:
            _database = self.database
        else:
            _database = database

        # If data is empty, not execute.
        if data in ([], [{}]):
            return

        # Generate SQL.
        data_flatten = {}
        sqls = []
        if where_fields == None:
            no_where = True
        else:
            no_where = False
            if where_fields.__class__ == str:
                where_fields = [where_fields]
        for index, row in enumerate(data):
            for key, val in row.items():
                index_key = "%d_%s" % (index, key)
                data_flatten[index_key] = val
            if no_where:
                where_fields = [list(row.keys())[0]]
            set_content = ",".join(
                [
                    "`%s` = :%d_%s" % (key, index, key)
                    for key in row
                    if key not in where_fields
                ]
            )
            where_content = "\n    AND ".join(
                [
                    f"`{field}` = :{index}_{field}"
                    for field in where_fields
                ]
            )
            sql = (
                f"UPDATE `{_database}`.`{table}`\n"
                f"SET {set_content}\n"
                f"WHERE {where_content}"
            )
            sqls.append(sql)
        sqls = ";\n".join(sqls)

        # Execute SQL.
        result = self.execute(sqls, data_flatten, report)

        return result


    def execute_insert(
        self,
        data: Union[CursorResult, List[Dict], Dict],
        table: str,
        database: Optional[str] = None,
        duplicate_method: Optional[Literal["ignore", "update"]] = None,
        report: bool = False
    ) -> Optional[CursorResult]:
        """
        Insert the data of table in the datebase.

        Parameters
        ----------
        data : Updated data.
        table : Table name.
        database : Database name.
        duplicate_method : Handle method when constraint error.
            - None : Not handled.
            - 'ignore' : Use 'UPDATE IGNORE INTO' clause.
            - 'update' : Use 'ON DUPLICATE KEY UPDATE' clause.

        report : Whether print SQL and execute run time.

        Returns
        -------
        None or CursorResult object.
            - None : When the data is empty.
            - CursorResult object : When the data is not empty.
        """

        # Handle parameters.
        if data.__class__ == CursorResult:
            data = self.to_table(data)
        elif data.__class__ == dict:
            data = [data]
        if database == None:
            _database = self.database
        else:
            _database = database

        # If data is empty, not execute.
        if data in ([], [{}]):
            return

        # Generate SQL.
        fields = list({key for row in data for key in row})
        fields_str = ",".join(["`%s`" % field for field in fields])
        fields_str_position = ",".join([":" + field for field in fields])
        if duplicate_method == "ignore":
            sql = (
                f"INSERT IGNORE INTO `{_database}`.`{table}`({fields_str})\n"
                f"VALUES({fields_str_position})"
            )
        elif duplicate_method == "update":
            update_content = ",".join(["`%s` = VALUES(`%s`)" % (field, field) for field in fields])
            sql = (
                f"INSERT INTO `{_database}`.`{table}`({fields_str})\n"
                f"VALUES({fields_str_position})\n"
                "ON DUPLICATE KEY UPDATE\n"
                f"{update_content}"
            )
        else:
            sql = (
                f"INSERT INTO `{_database}`.`{table}`({fields_str})\n"
                f"VALUES({fields_str_position})"
            )

        # Execute SQL.
        result = self.execute(sql, data, report)

        return result


    @overload
    def execute_exist(
        self,
        table: str,
        database: Optional[str] = None,
        where: Optional[str] = None,
        count: bool = False
    ) -> Union[bool, int]: ...

    @overload
    def execute_exist(
        self,
        count: Literal[False]
    ) -> bool: ...

    @overload
    def execute_exist(
        self,
        count: Literal[True]
    ) -> int: ...

    def execute_exist(
        self,
        table: str,
        database: Optional[str] = None,
        where: Optional[str] = None,
        count: bool = False
    ) -> Union[bool, int]:
        """
        Count records.

        Parameters
        ----------
        table : Table name.
        database : Database name.
        where : Match condition, 'WHERE' clause content, join as 'WHERE str'.
            - None : Match all.
            - str : Match condition.

        count : Whether return match count, otherwise return whether it exist.

        Returns
        -------
        CursorResult object of alsqlchemy package.
        """

        # Get parameters.
        if count:
            limit = None
        else:
            limit = 1

        # Execute.
        result = self.execute_select(table, database, "1", where=where, limit=limit)
        rowcount = result.rowcount

        # Returns.
        if count:
            return rowcount
        else:
            return bool(rowcount)


    def connect(self):
        """
        Create database connection object.
        """

        rconnection = RConnection(
            self.engine.connect(),
            self
        )

        return rconnection


class RConnection(REngine):
    """
    Rey's database Connection type, based on the package sqlalchemy.
    """


    def __init__(
            self,
            connection: Connection,
            rengine: REngine,

        ) -> None:
        """
        Create database connection object and set parameters.

        Parameters
        ----------
        connection : Connection object.
        rengine : REngine object.
        """

        self.connection = connection
        self.rengine = rengine
        self.begin = None
        self.begin_count = 0
        self.drivername = rengine.drivername
        self.username = rengine.username
        self.password = rengine.password
        self.host = rengine.host
        self.port = rengine.port
        self.database = rengine.database
        self.query = rengine.query
        self.recycle = rengine.recycle


    def commit(self) -> None:
        """
        Commit cumulative executions.
        """

        # Commit.
        if self.begin != None:
            self.begin.commit()
            self.begin = None
            self.begin_count = 0


    def rollback(self) -> None:
        """
        Rollback cumulative executions.
        """

        # Rollback.
        if self.begin != None:
            self.begin.rollback()
            self.begin = None
            self.begin_count = 0


    def close(self) -> None:
        """
        Close database connection.
        """

        self.connection.close()


    def __del__(self) -> None:
        """
        Close database connection.
        """

        self.close()