import math
import os
import re
import sqlite3
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import exc, pool
from sqlalchemy import types as sqltypes
from sqlalchemy import util
from sqlalchemy.dialects.sqlite.base import DATE, DATETIME
from sqlalchemy.dialects.sqlite.base import SQLiteDialect as _SQLiteDialect
from sqlalchemy.engine import AdaptedConnection
from sqlalchemy.util.concurrency import await_fallback, await_only

executor = ThreadPoolExecutor(max_workers=1)


class _SQLite_TimeStamp(DATETIME):

    def bind_processor(self, dialect):
        if dialect.native_datetime:
            return None
        else:
            return DATETIME.bind_processor(self, dialect)

    def result_processor(self, dialect, coltype):
        if dialect.native_datetime:
            return None
        else:
            return DATETIME.result_processor(self, dialect, coltype)


class _SQLite_Date(DATE):

    def bind_processor(self, dialect):
        if dialect.native_datetime:
            return None
        else:
            return DATE.bind_processor(self, dialect)

    def result_processor(self, dialect, coltype):
        if dialect.native_datetime:
            return None
        else:
            return DATE.result_processor(self, dialect, coltype)


class Cursor:
    __slots__ = (
        "_adapt_connection",
        "_connection",
        "description",
        "await_",
        "_rows",
        "arraysize",
        "rowcount",
        "lastrowid",
    )

    server_side = False

    def __init__(self, adapt_connection):
        self._adapt_connection = adapt_connection
        self._connection = adapt_connection._connection
        self.await_ = adapt_connection.await_
        self.arraysize = 1
        self.rowcount = -1
        self.description = None
        self._rows = []

    def close(self):
        self._rows[:] = []

    def execute(self, operation, parameters=None):
        try:
            _cursor = self.await_(self._connection.cursor())

            if parameters is None:
                self.await_(_cursor.execute(operation))
            else:
                self.await_(_cursor.execute(operation, parameters))

            if _cursor.description:
                self.description = _cursor.description
                self.lastrowid = self.rowcount = -1

                if not self.server_side:
                    self._rows = self.await_(_cursor.fetchall())
            else:
                self.description = None
                self.lastrowid = _cursor.lastrowid
                self.rowcount = _cursor.rowcount

            if not self.server_side:
                self.await_(_cursor.close())
            else:
                self._cursor = _cursor
        except Exception as error:
            self._adapt_connection._handle_exception(error)

    def executemany(self, operation, seq_of_parameters):
        try:
            _cursor = self.await_(self._connection.cursor())
            self.await_(_cursor.executemany(operation, seq_of_parameters))
            self.description = None
            self.lastrowid = _cursor.lastrowid
            self.rowcount = _cursor.rowcount
            self.await_(_cursor.close())
        except Exception as error:
            self._adapt_connection._handle_exception(error)

    def setinputsizes(self, *inputsizes):
        pass

    def __iter__(self):
        while self._rows:
            yield self._rows.pop(0)

    def fetchone(self):
        if self._rows:
            return self._rows.pop(0)
        else:
            return None

    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize

        retval = self._rows[0:size]
        self._rows[:] = self._rows[size:]
        return retval

    def fetchall(self):
        retval = self._rows[:]
        self._rows[:] = []
        return retval


class ServerSideCursor(Cursor):
    __slots__ = "_cursor"

    server_side = True

    def __init__(self, *arg, **kw):
        super().__init__(*arg, **kw)
        self._cursor = None

    def close(self):
        if self._cursor is not None:
            self.await_(self._cursor.close())
            self._cursor = None

    def fetchone(self):
        return self.await_(self._cursor.fetchone())

    def fetchmany(self, size=None):
        if size is None:
            size = self.arraysize
        return self.await_(self._cursor.fetchmany(size=size))

    def fetchall(self):
        return self.await_(self._cursor.fetchall())


class Connection(AdaptedConnection):
    await_ = staticmethod(await_only)
    __slots__ = ("dbapi", )

    def __init__(self, dbapi, connection):
        self.dbapi = dbapi
        self._connection = connection

    @property
    def isolation_level(self):
        return self._connection.isolation_level

    @isolation_level.setter
    def isolation_level(self, value):
        try:
            self._connection.isolation_level = value
        except Exception as error:
            self._handle_exception(error)

    def create_function(self, *args, **kw):
        try:
            self.await_(self._connection.create_function(*args, **kw))
        except Exception as error:
            self._handle_exception(error)

    def cursor(self, server_side=False):
        if server_side:
            return ServerSideCursor(self)
        else:
            return Cursor(self)

    def execute(self, *args, **kw):
        return self.await_(self._connection.execute(*args, **kw))

    def rollback(self):
        try:
            self.await_(self._connection.rollback())
        except Exception as error:
            self._handle_exception(error)

    def commit(self):
        try:
            self.await_(self._connection.commit())
        except Exception as error:
            self._handle_exception(error)

    def close(self):
        # print(">close", self)
        try:
            self.await_(self._connection.close())
        except Exception as error:
            self._handle_exception(error)

    def _handle_exception(self, error):
        if (isinstance(error, ValueError)
                and error.args[0] == "no active connection"):
            raise self.dbapi.sqlite.OperationalError(
                "no active connection") from error
        else:
            raise error


class FallbackConnection(Connection):
    __slots__ = ()

    await_ = staticmethod(await_fallback)


class Sqlite_dbapi:

    def __init__(self):
        self.paramstyle = "qmark"
        self._init_dbapi_attributes()

    def _init_dbapi_attributes(self):
        for name in (
                "Binary",
                "DatabaseError",
                "Error",
                "IntegrityError",
                "NotSupportedError",
                "OperationalError",
                "ProgrammingError",
                "sqlite_version",
                "sqlite_version_info",
        ):
            setattr(self, name, getattr(sqlite3, name))

        for name in ("PARSE_COLNAMES", "PARSE_DECLTYPES"):
            setattr(self, name, getattr(sqlite3, name))

    def connect(self, *arg, **kw):
        return sqlite3.connect(*arg, **kw)


class SQLiteDialect(_SQLiteDialect):
    default_paramstyle = "qmark"
    supports_statement_cache = True

    colspecs = util.update_copy(
        _SQLiteDialect.colspecs,
        {
            sqltypes.Date: _SQLite_Date,
            sqltypes.TIMESTAMP: _SQLite_TimeStamp,
        },
    )

    description_encoding = None

    driver = "mydriver"

    #@classmethod
    #def import_dbapi(cls):
    #    return Sqlite_dbapi()

    @classmethod
    def dbapi(cls):
        return Sqlite_dbapi()
        #return cls.import_dbapi()

    @classmethod
    def _is_url_file_db(cls, url):
        if (url.database and url.database != ":memory:") and (url.query.get(
                "mode", None) != "memory"):
            return True
        else:
            return False

    @classmethod
    def get_pool_class(cls, url):
        if cls._is_url_file_db(url):
            return pool.QueuePool
        else:
            return pool.SingletonThreadPool

    def _get_server_version_info(self, connection):
        return self.dbapi.sqlite_version_info

    _isolation_lookup = _SQLiteDialect._isolation_lookup.union({
        "AUTOCOMMIT":
        None,
    })

    def set_isolation_level(self, dbapi_connection, level):

        if level == "AUTOCOMMIT":
            dbapi_connection.isolation_level = None
        else:
            dbapi_connection.isolation_level = ""
            return super().set_isolation_level(dbapi_connection, level)

    def on_connect(self):

        def regexp(a, b):
            if b is None:
                return None
            return re.search(a, b) is not None

        create_func_kw = {"deterministic": True} if util.py38 else {}

        def set_regexp(dbapi_connection):
            dbapi_connection.create_function("regexp", 2, regexp,
                                             **create_func_kw)

        def floor_func(dbapi_connection):
            # NOTE: floor is optionally present in sqlite 3.35+ , however
            # as it is normally non-present we deliver floor() unconditionally
            # for now.
            # https://www.sqlite.org/lang_mathfunc.html
            dbapi_connection.create_function("floor", 1, math.floor,
                                             **create_func_kw)

        fns = [set_regexp, floor_func]

        def connect(conn):
            for fn in fns:
                fn(conn)

        return connect

    def create_connect_args(self, url):
        if url.username or url.password or url.host or url.port:
            raise exc.ArgumentError("Invalid SQLite URL: %s\n"
                                    "Valid SQLite URL forms are:\n"
                                    " sqlite:///:memory: (or, sqlite://)\n"
                                    " sqlite:///relative/path/to/file.db\n"
                                    " sqlite:////absolute/path/to/file.db" %
                                    (url, ))

        # theoretically, this list can be augmented, at least as far as
        # parameter names accepted by sqlite3/pysqlite, using
        # inspect.getfullargspec().  for the moment this seems like overkill
        # as these parameters don't change very often, and as always,
        # parameters passed to connect_args will always go to the
        # sqlite3/pysqlite driver.
        pysqlite_args = [
            ("uri", bool),
            ("timeout", float),
            ("isolation_level", str),
            ("detect_types", int),
            ("check_same_thread", bool),
            ("cached_statements", int),
        ]
        opts = url.query
        pysqlite_opts = {}
        for key, type_ in pysqlite_args:
            util.coerce_kw_type(opts, key, type_, dest=pysqlite_opts)

        if pysqlite_opts.get("uri", False):
            uri_opts = dict(opts)
            # here, we are actually separating the parameters that go to
            # sqlite3/pysqlite vs. those that go the SQLite URI.  What if
            # two names conflict?  again, this seems to be not the case right
            # now, and in the case that new names are added to
            # either side which overlap, again the sqlite3/pysqlite parameters
            # can be passed through connect_args instead of in the URL.
            # If SQLite native URIs add a parameter like "timeout" that
            # we already have listed here for the python driver, then we need
            # to adjust for that here.
            for key, type_ in pysqlite_args:
                uri_opts.pop(key, None)
            filename = url.database
            if uri_opts:
                # sorting of keys is for unit test support
                filename += "?" + ("&".join("%s=%s" % (key, uri_opts[key])
                                            for key in sorted(uri_opts)))
        else:
            filename = url.database or ":memory:"
            if filename != ":memory:":
                filename = os.path.abspath(filename)

        pysqlite_opts.setdefault("check_same_thread",
                                 not self._is_url_file_db(url))

        return ([filename], pysqlite_opts)

    def is_disconnect(self, e, connection, cursor):
        return isinstance(
            e, self.dbapi.ProgrammingError
        ) and "Cannot operate on a closed database." in str(e)
