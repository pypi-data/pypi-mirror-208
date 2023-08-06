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
from sqlalchemy.engine.base import Engine, Connection
from sqlalchemy.engine.cursor import CursorResult
from sqlalchemy.engine.url import URL
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.exc import OperationalError

from .rbase import get_first_notnull
from .rdata import to_table
from .rmonkey import sqlalchemy_add_result_more_fetch, sqlalchemy_support_row_index_by_field
from .rother import str2n
from .rregular import re_search
from .rtext import rprint
from .rwrap import runtime, retry


# Add more fetch methods to CursorResult object.
RResult = sqlalchemy_add_result_more_fetch()

# Support Row object of package sqlalchemy index by field name.
sqlalchemy_support_row_index_by_field()


class REngine(object):
    """
    Rey's database `Engine` type, based on the package `sqlalchemy`.
    """

    # Values to be converted to "NULL".
    null_values: ClassVar[List] = ["", " ", b"", [], (), {}, set()]


    @overload
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        drivername: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: float = 30.0,
        pool_recycle: Optional[int] = None,
        url: Optional[Union[str, URL]] = None,
        engine: Optional[Union[Engine, Connection]] = None,
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
        host: Optional[str] = None,
        port: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        drivername: Optional[str] = None,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: float = 30.0,
        pool_recycle: Optional[int] = None,
        url: Optional[Union[str, URL]] = None,
        engine: Optional[Union[Engine, Connection]] = None,
        **query: str
    ) -> None:
        """
        Create database `Engine` object and set parameters.

        Parameters
        ----------
        host : Server host.
        port : Server port.
        username : Server user name.
        password : Server password.
        database : Database name in the server.
        drivername : Database backend and driver name.
            - `None` : Auto select and try.
            - `str` : Use this value.

        pool_size : Number of connections `keep open`.
        max_overflow : Number of connections `allowed overflow`.
        pool_timeout : Number of seconds `wait create` connection.
        pool_recycle : Number of seconds `recycle` connection.
            - `None` : Use database variable `wait_timeout` value.
            - `Literal[-1]` : No recycle.
            - `int` : Use this value.

        url: Get parameters from server `URL`, but preferred input parameters.
            Parameters include `username`, `password`, `host`, `port`, `database`, `drivername`, `query`.
        engine : Use existing `Engine` or `Connection` object, and get parameters from it.
            Parameters include `username`, `password`, `host`, `port`, `database`, `drivername`, `query`,
            `pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`.
        query : Server parameters.
        """

        # From existing Engine or Connection object.
        if engine != None:

            ## Extract Engine object from Connection boject.
            if engine.__class__ == Connection:
                engine = engine.engine

            ## Extract parameters.
            params = self.extract_from_engine(engine)

            ## Set.
            self.drivername = params["drivername"]
            self.username = params["username"]
            self.password = params["password"]
            self.host = params["host"]
            self.port = params["port"]
            self.database = params["database"]
            self.query = params["query"]
            self.pool_size = params["pool_size"]
            self.max_overflow = params["max_overflow"]
            self.pool_timeout = params["pool_timeout"]
            self.pool_recycle = params["pool_recycle"]
            self.engine = engine

        # From parameters create.
        else:

            ## Extract parameters from URL.
            if url != None:
                params = self.extract_from_url(url)
            else:
                params = dict.fromkeys(
                    (
                        "drivername",
                        "username",
                        "password",
                        "host",
                        "port",
                        "database",
                        "query"
                    )
                )

            ## Set parameters by priority.
            self.drivername = get_first_notnull(drivername, params["drivername"])
            self.username = get_first_notnull(username, params["username"], default="error")
            self.password = get_first_notnull(password, params["password"], default="error")
            self.host = get_first_notnull(host, params["host"], default="error")
            self.port = get_first_notnull(port, params["port"], default="error")
            self.database = get_first_notnull(database, params["database"])
            self.query = get_first_notnull(query, params["query"], default={"charset": "utf8"}, null_values=[None, {}])
            self.pool_size = pool_size
            self.max_overflow = max_overflow
            self.pool_timeout = pool_timeout

            ## Create Engine object.

            ### Set number of seconds recycle connection.
            if pool_recycle == None:
                self.pool_recycle = -1
                self.engine = self.create_engine()
                variables = self.get_variable()
                self.pool_recycle = int(variables["wait_timeout"])
                self.engine.pool._recycle = int(variables["wait_timeout"])

            else:
                self.pool_recycle = pool_recycle
                self.engine = self.create_engine()


    def extract_from_url(self, url: Union[str, URL]) -> Dict[
        Literal["drivername", "username", "password", "host", "port", "database", "query"],
        Optional[Union[str, Dict[str, str]]]
    ]:
        """
        Extract parameters from `URL` of string.

        Parameters
        ----------
        url : URL of string.

        Returns
        -------
        Extracted parameters.
        """

        # Extract.

        ## When str object.
        if url.__class__ == str:
            pattern = "^([\w\+]+)://(\w+):(\w+)@(\d+\.\d+\.\d+\.\d+):(\d+)[/]?([\w/]+)?[\?]?([\w&=]+)?$"
            result = re_search(pattern, url)
            if result == None:
                raise ValueError("the value of parameter 'url' is incorrect")
            (
                drivername,
                username,
                password,
                host,
                port,
                database,
                query_str
            ) = result
            if query_str != None:
                pattern = "(\w+)=(\w+)"
                query_findall = findall(pattern, query_str)
                query = {key: val for key, val in query_findall}
            else:
                query = {}

        ## When URL object.
        elif url.__class__ == URL:
            drivername = url.drivername
            username = url.username
            password = url.password
            host = url.host
            port = url.port
            database = url.database
            query = dict(url.query)

        # Generate parameters.
        params = {
            "drivername": drivername,
            "username": username,
            "password": password,
            "host": host,
            "port": port,
            "database": database,
            "query": query
        }

        return params


    def extract_from_engine(self, engine: Union[Engine, Connection]) -> Dict[
        Literal[
            "drivername", "username", "password", "host", "port", "database", "query",
            "pool_size", "max_overflow", "pool_timeout", "pool_recycle"
        ],
        Optional[Union[str, Dict[str, str], float]]
    ]:
        """
        Extract parameters from `Engine` or `Connection` object.

        Parameters
        ----------
        engine : Engine or Connection object.

        Returns
        -------
        Extracted parameters.
        """

        ## Extract Engine object from Connection boject.
        if engine.__class__ == Connection:
            engine = engine.engine

        ## Extract.
        drivername = engine.url.drivername
        username = engine.url.username
        password = engine.url.password
        host = engine.url.host
        port = engine.url.port
        database = engine.url.database
        query = dict(engine.url.query)
        pool_size = engine.pool._pool.maxsize
        max_overflow = engine.pool._max_overflow
        pool_timeout = engine.pool._timeout
        pool_recycle = engine.pool._recycle

        # Generate parameters.
        params = {
            "drivername": drivername,
            "username": username,
            "password": password,
            "host": host,
            "port": port,
            "database": database,
            "query": query,
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle
        }

        return params


    def url(self) -> str:
        """
        Generate server `URL`.

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
        Create database `Engine` object.

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

            ## Try create.
            try:
                engine = sqlalchemy_create_engine(
                    url,
                    pool_size=self.pool_size,
                    max_overflow=self.max_overflow,
                    pool_timeout=self.pool_timeout,
                    pool_recycle=self.pool_recycle
                )
            except ModuleNotFoundError:
                pass
            else:
                return engine

        # Throw error.
        drivernames_str = " and ".join(
            [
                dirvername.split("+", 1)[-1]
                for dirvername in drivernames
            ]
        )
        raise ModuleNotFoundError("module %s not fund" % drivernames_str)


    def count_connection(self) -> Tuple[int, int]:
        """
        Count number of `keep open` and `allowed overflow` connection.

        Returns
        -------
        Number of keep open and allowed overflow connection.
        """

        # Count.
        _overflow = self.engine.pool._overflow
        if _overflow < 0:
            keep_n = self.pool_size + _overflow
            overflow_n = 0
        else:
            keep_n = self.pool_size
            overflow_n = _overflow

        return keep_n, overflow_n


    def fill_data(
        self,
        data: Union[Dict, List[Dict]],
        sql: Union[str, TextClause],
    ) -> List[Dict]:
        """
        `Fill` missing data according to contents of `TextClause` object of package `sqlalchemy`, and filter out empty Dict.

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
        Extract `syntax` type form SQL.

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
    ) -> RResult:
        """
        Execute `SQL` and `report` result.

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
        connection: Connection,
        sql: TextClause,
        data: List[Dict],
        report: bool = False
    ) -> RResult:
        """
        `SQL` executor.

        Parameters
        ----------
        connection : Connection object.
        sql : TextClause object.
        data : Data set for filling.
        report : Whether print SQL and execute run time.

        Returns
        -------
        CursorResult object of alsqlchemy package.
        """

        # When REngine.
        if self.__class__ == REngine:

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
                self.rollback()
                self.begin = connection.begin()

            ## Execute.
            if report:
                result = self.execute_report(connection, sql, data)
            else:
                result = connection.execute(sql, data)

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
    ) -> RResult:
        """
        Execute `SQL`.

        Parameters
        ----------
        sql : SQL in method `sqlalchemy.text` format, or `TextClause` object.
        data : Data set for filling.
        report : Whether print SQL and execute run time.
        kwdata : Keyword data for filling `sqlalchemy.text`.

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

            ### Create Connection object.
            with self.engine.connect() as connection:

                ### Can retry.
                result = retry(
                    self.executor,
                    connection,
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
                self.connection,
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
        ) -> RResult:
        """
        Execute `select` SQL.

        Parameters
        ----------
        table : Table name.
        database : Database name.
        fields : Select clause content.
            - `None` : Is `SELECT *`.
            - `str` : Join as `SELECT str`.
            - `Iterable[str]` : Join as `SELECT \`str\`, ...`.

        where : Clause `WHERE` content, join as `WHERE str`.
        group : Clause `GROUP BY` content, join as `GROUP BY str`.
        having : Clause `HAVING` content, join as `HAVING str`.
        order : Clause `ORDER BY` content, join as `ORDER BY str`.
        limit : Clause `LIMIT` content.
            - `Union[int, str]` : Join as `LIMIT int/str`.
            - `Union[List, Tuple]` with length of 1 or 2 `int/str` : Join as `LIMIT int/str [, int/str]`.

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
    ) -> Optional[RResult]:
        """
        `Update` the data of table in the datebase.

        Parameters
        ----------
        data : Updated data.
        table : Table name.
        database : Database name.
        where_fields : Clause `WHERE` clause content.
            - `None` : The first key value pair of each item is judged.
            - `str` : This key value pair of each item is judged.
            - `Iterable[str]` : Multiple judged, `and` relationship.

        report : Whether print SQL and execute run time.

        Returns
        -------
        None or CursorResult object.
            - `None` : When the data is empty.
            - `CursorResult object` : When the data is not empty.
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
    ) -> Optional[RResult]:
        """
        `Insert` the data of table in the datebase.

        Parameters
        ----------
        data : Updated data.
        table : Table name.
        database : Database name.
        duplicate_method : Handle method when constraint error.
            - `None` : Not handled.
            - `ignore` : Use `UPDATE IGNORE INTO` clause.
            - `update` : Use `ON DUPLICATE KEY UPDATE` clause.

        report : Whether print SQL and execute run time.

        Returns
        -------
        None or CursorResult object.
            - `None` : When the data is empty.
            - `CursorResult` object : When the data is not empty.
        """

        # Handle parameters.
        if isinstance(data, CursorResult):
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
        `Count` records.

        Parameters
        ----------
        table : Table name.
        database : Database name.
        where : Match condition, `WHERE` clause content, join as `WHERE str`.
            - `None` : Match all.
            - `str` : Match condition.

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


    def get_variable(self, global_: bool = False) -> Dict:
        """
        Get `variables` of database.

        Parameters
        ----------
        global_ : Whether get global variable, otherwise get local variable.
        """

        # Generate SQL.
        if global_:
            sql = """
            SHOW GLOBAL VARIABLES
            """
        else:
            sql = """
            SHOW VARIABLES
            """

        # Execute SQL.
        result = self.execute(sql)

        # Convert dictionary.
        variables = {key: str2n(val) for key, val in result}

        return variables


    def get_status(self, global_: bool = False) -> Dict:
        """
        Get `status` of database.

        Parameters
        ----------
        global_ : Whether get global variable, otherwise get local variable.
        """

        # Generate SQL.
        if global_:
            sql = """
            SHOW GLOBAL STATUS
            """
        else:
            sql = """
            SHOW STATUS
            """

        # Execute SQL.
        result = self.execute(sql)

        # Convert dictionary.
        status = {key: str2n(val) for key, val in result}

        return status


    def update_variable(self, params: Dict[str, Union[str, float]], global_: bool = False) -> None:
        """
        Update `variables` of database.

        Parameters
        ----------
        params : Update parameter key value pairs.
        global_ : Whether update global variable, otherwise update local variable.
        """

        # Generate SQL.
        if global_:
            sql_global = " GLOBAL"
        else:
            sql_global = ""
        sqls = [
            "SET%s %s = %s" % (
                sql_global,
                key,
                (
                    val
                    if val.__class__ in (int, float)
                    else "'%s'" % val
                )
            )
            for key, val in params.items()
        ]
        sqls = ";\n".join(sqls)

        # Execute SQL.
        self.execute(sqls)


    def connect(self):
        """
        Create database `Connection` object.
        """

        rconnection = RConnection(
            self.engine.connect(),
            self
        )

        return rconnection


class RConnection(REngine):
    """
    Rey's database `Connection` type, based on the package `sqlalchemy`.
    """


    def __init__(
            self,
            connection: Connection,
            rengine: REngine,

        ) -> None:
        """
        Create database `Connection` object and set parameters.

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
        self.pool_recycle = rengine.pool_recycle


    def commit(self) -> None:
        """
        `Commit` cumulative executions.
        """

        # Commit.
        if self.begin != None:
            self.begin.commit()
            self.begin = None
            self.begin_count = 0


    def rollback(self) -> None:
        """
        `Rollback` cumulative executions.
        """

        # Rollback.
        if self.begin != None:
            self.begin.rollback()
            self.begin = None
            self.begin_count = 0


    def close(self) -> None:
        """
        `Close` database connection.
        """

        # Close.
        self.connection.close()


    def __del__(self) -> None:
        """
        `Close` database connection.
        """

        # Close.
        self.close()