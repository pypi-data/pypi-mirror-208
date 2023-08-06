# encoding: utf-8
import time
import sqlite3
import threading
from pymysql.converters import escape_string
from pymysql import (connect, cursors, err)
import uuid


class ScriptRunner:

    def __init__(self, connection, delimiter=";", autocommit=True):
        self.connection = connection
        self.delimiter = delimiter
        self.autocommit = autocommit

    def run_script(self, sql):
        try:
            script = ""
            for line in sql.splitlines():
                strip_line = line.strip()
                if "DELIMITER $$" in strip_line:
                    self.delimiter = "$$"
                    continue
                if "DELIMITER ;" in strip_line:
                    self.delimiter = ";"
                    continue

                if strip_line and not strip_line.startswith("//") and not strip_line.startswith("--"):
                    script += line + "\n"
                    if strip_line.endswith(self.delimiter):
                        if self.delimiter == "$$":
                            script = script[:-1].rstrip("$") + ";"
                        cursor = self.connection.cursor()
                        print(script)
                        cursor.execute(script)
                        script = ""

            if script.strip():
                raise Exception("Line missing end-of-line terminator (" + self.delimiter + ") => " + script)

            if not self.connection.get_autocommit():
                self.connection.commit()
        except Exception:
            if not self.connection.get_autocommit():
                self.connection.rollback()
            raise


class Dict(dict):
    """
    Simple dict but support access as x.y style.
    >>> d1 = Dict()
    >>> d1['x'] = 100
    >>> d1.x
    100
    >>> d1.y = 200
    >>> d1['y']
    200
    >>> d2 = Dict(a=1, b=2, c='3')
    >>> d2.c
    '3'
    >>> d2['empty']
    Traceback (most recent call last):
        ...
    KeyError: 'empty'
    >>> d2.empty
    Traceback (most recent call last):
        ...
    AttributeError: 'Dict' object has no attribute 'empty'
    >>> d3 = Dict(('a', 'b', 'c'), (1, 2, 3))
    >>> d3.a
    1
    >>> d3.b
    2
    >>> d3.c
    3

    """

    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def next_id(t=None):
    """
    Return next id as 50-char string.
    Args:
        t: unix timestamp, default to None and using time.time().
    """
    if t is None:
        t = time.time()
    return '%015d%s000' % (int(t * 1000), uuid.uuid4().hex)


def join_field_value(data, glue=', '):
    sql = comma = ''
    for key in data.keys():
        sql += "{}`{}` = ?".format(comma, key)
        comma = glue
    return sql


def join_field(data, glue=', '):
    sql = comma = ''
    for key in data.keys():
        sql += "{}`{}`".format(comma, key)
        comma = glue
    return sql


def join_value(data, glue=', '):
    sql = comma = ''
    for key in data.values():
        sql += "{}?".format(comma, key)
        comma = glue
    return sql


class SQLite:
    """A Friendly pysqlite Class, Provide CRUD functionality"""

    def __init__(self, filepath):
        self.filepath = filepath
        self.connection = self.session()
        self.lock = threading.Lock()

    def session(self):
        """Connect to the database return dbsession"""
        connection = sqlite3.connect(self.filepath, check_same_thread=False)
        return connection

    def replace(self, table, data):
        """sqlite replace() function"""
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            fields = join_field(data)
            values = join_value(data)

            sql = "INSERT OR REPLACE INTO {table} ({fields}) VALUES ({values})".format(
                table=table, fields=fields, values=values)

            cursor.execute(sql, tuple(data.values()))
            last_id = cursor.lastrowid

            self.connection.commit()
            return last_id

        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def insert(self, table, data):
        """sqlite insert() function"""
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            fields = join_field(data)
            values = join_value(data)

            sql = "INSERT OR IGNORE INTO {table} ({fields}) VALUES ({values})".format(
                table=table, fields=fields, values=values)

            cursor.execute(sql, tuple(data.values()))
            last_id = cursor.lastrowid

            self.connection.commit()
            return last_id

        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def bulk_insert(self, table, data):

        assert isinstance(data, list) and data != [], "data_format_error"
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            params = []
            for param in data:
                params.append(param.values().replace("'", "''"))

            values = ', '.join(params)
            fields = ', '.join('`{}`'.format(x) for x in params.keys())

            sql = "INSERT OR IGNORE INTO {table} ({fields}) VALUES {values}".format(
                fields=fields, table=table, values=values)

            cursor.execute(sql)
            last_id = cursor.lastrowid

            self.connection.commit()
            return last_id

        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def delete(self, table, condition=None, limit=None):
        """
        sqlite delete() function
        sql.PreparedStatement method
        """
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()

            prepared = []

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            limits = "LIMIT {limit}".format(limit=limit) if limit else ""

            sql = "DELETE FROM {table} WHERE {where} {limits}".format(
                table=table, where=where, limits=limits)

            if not prepared:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return result

        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def update(self, table, data, condition=None):
        """
        sqlite update() function
        Use sql.PreparedStatement method
        """
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()

            prepared = []
            params = join_field_value(data)
            prepared.extend(data.values())

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            sql = "UPDATE OR IGNORE {table} SET {params} WHERE {where}".format(
                table=table, params=params, where=where)

            # check PreparedStatement
            if not prepared:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return result.rowcount

        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def count(self, table, condition=None, *parameters):
        """
        count database record
        Use sql.PreparedStatement method
        """
        prepared = []

        if not condition:
            where = '1'
        elif isinstance(condition, dict):
            where = join_field_value(condition, ' AND ')
            prepared.extend(condition.values())
        else:
            where = condition
            prepared = list(parameters)

        sql = "SELECT COUNT(*) as cnt FROM {table} WHERE {where}".format(
            table=table, where=where)

        if not prepared:
            result = self.get(sql)
        else:
            result = self.get(sql, *prepared)

        return result.get('cnt')

    def fetch_rows(self, table, fields=None, condition=None, order=None, limit=None, fetchone=False):
        """
        sqlite select() function
        Use sql.PreparedStatement method
    """

        prepared = []

        if not fields:
            fields = '*'
        elif isinstance(fields, tuple) or isinstance(fields, list):
            fields = '`{0}`'.format('`, `'.join(fields))
        else:
            fields = fields

        if not condition:
            where = '1'
        elif isinstance(condition, dict):
            where = join_field_value(condition, ' AND ')
            prepared.extend(condition.values())
        else:
            where = condition

        if not order:
            orderby = ''
        else:
            orderby = 'ORDER BY {order}'.format(order=order)

        limits = "LIMIT {limit}".format(limit=limit) if limit else ""

        sql = "SELECT {fields} FROM {table} WHERE {where} {orderby} {limits}".format(
            fields=fields, table=table, where=where, orderby=orderby, limits=limits)

        if not prepared:
            if fetchone:
                result = self.get(sql)
            else:
                result = self.query(sql)
        else:

            if fetchone:
                result = self.get(sql, *prepared)
            else:
                result = self.query(sql, *prepared)
        return result

    def get(self, sql, *parameters, **kwparameters):
        """查询sql获取单行记录"""
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, kwparameters or parameters)
            if cursor.description:
                names = [x[0] for x in cursor.description]
            values = cursor.fetchone()
            self.connection.commit()
            if not values:
                return None
            return Dict(names, values)
        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def execute(self, sql, *parameters, **kwparameters):
        """执行给定的查询，从查询返回lastrowid"""
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, kwparameters or parameters)
            self.connection.commit()
            return cursor.lastrowid
        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def query(self, sql, *parameters, **kwparameters):
        """execute custom sql query"""
        cursor = None
        self.lock.acquire()
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql, kwparameters or parameters)
            self.connection.commit()
            if cursor.description:
                names = [x[0] for x in cursor.description]
            return [Dict(names, x) for x in cursor.fetchall()]
        finally:
            if cursor:
                cursor.close()
            self.lock.release()

    def fetchone(self, table, fields=None, condition=None, order=None, limit=None):
        return self.fetch_rows(table, fields, condition, order, limit, True)

    def close(self):
        if getattr(self, 'connection', 0):
            return self.connection.close()

    def __del__(self):
        """close sqlite database connection"""
        self.close()


def connect_db(mysqldb_conn):
    # msyql dababase connection info
    dbconn = MYSQL(
        dbhost=mysqldb_conn.get('host'),
        dbport=mysqldb_conn.get('port'),
        dbuser=mysqldb_conn.get('user'),
        dbpwd=mysqldb_conn.get('password'),
        dbname=mysqldb_conn.get('db'),
        dbcharset=mysqldb_conn.get('charset'))
    return dbconn


def connect_ssdc(mysqldb_conn):
    """Connect to the database return SSDictCursor dbsession"""
    connection = connect(
        host=mysqldb_conn.get('host'),
        port=int(mysqldb_conn.get('port')) or 3306,
        user=mysqldb_conn.get('user'),
        password=mysqldb_conn.get('password'),
        db=mysqldb_conn.get('db'),
        charset=mysqldb_conn.get('charset'),
        cursorclass=cursors.SSDictCursor)
    return connection


class MYSQL:
    """A Friendly pymysql Class, Provide CRUD functionality"""

    def __init__(self, dbhost, dbuser, dbpwd, dbname, dbcharset='utf8mb4', dbport=3306):
        self.dbhost = dbhost
        self.dbport = int(dbport)
        self.dbuser = dbuser
        self.dbpwd = dbpwd
        self.dbname = dbname
        self.dbcharset = dbcharset
        self.connection = self.session()

    def session(self):
        """Connect to the database return dbsession"""
        connection = connect(
            host=self.dbhost,
            port=self.dbport,
            user=self.dbuser,
            password=self.dbpwd,
            db=self.dbname,
            charset=self.dbcharset,
            cursorclass=cursors.DictCursor)
        return connection

    def replace(self, table, data):
        """mysql replace() function"""

        with self.connection.cursor() as cursor:

            params = self.join_field_value(data)

            sql = "REPLACE INTO {table} SET {params}".format(
                table=table, params=params)

            cursor.execute(sql, tuple(data.values()))
            # last_id = self.connection.insert_id() 并发情况下可能不准
            last_id = cursor.lastrowid

            self.connection.commit()
            return last_id

    def insert(self, table, data):
        """mysql insert() function"""

        with self.connection.cursor() as cursor:

            values = ', '.join('%s' for x in data.values())
            fields = ', '.join('`{}`'.format(x) for x in data.keys())

            sql = "INSERT IGNORE INTO {table} ({fields}) VALUES ({values})".format(
                fields=fields, table=table, values=values)

            cursor.execute(sql, tuple(data.values()))
            last_id = cursor.lastrowid

            self.connection.commit()
            return last_id

    def bulk_insert(self, table, data):

        assert isinstance(data, list) and data != [], "data_format_error"

        with self.connection.cursor() as cursor:

            params = []
            for param in data:
                params.append(escape_string(param.values(), 'utf-8'))

            values = ', '.join(params)
            fields = ', '.join('`{}`'.format(x) for x in params.keys())

            sql = "INSERT IGNORE INTO {table} ({fields}) VALUES {values}".format(
                fields=fields, table=table, values=values)

            cursor.execute(sql)
            last_id = cursor.lastrowid

            self.connection.commit()
            return last_id

    def delete(self, table, condition=None, limit=None):
        """
        mysql delete() function
        sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            limits = "LIMIT {limit}".format(limit=limit) if limit else ""

            sql = "DELETE FROM {table} WHERE {where} {limits}".format(
                table=table, where=where, limits=limits)

            if not prepared:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return result

    def update(self, table, data, condition=None):
        """
        mysql update() function
        Use sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []
            params = self.join_field_value(data)
            prepared.extend(data.values())

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            sql = "UPDATE IGNORE {table} SET {params} WHERE {where}".format(
                table=table, params=params, where=where)

            # check PreparedStatement
            if not prepared:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return result

    def count(self, table, condition=None):
        """
        count database record
        Use sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            sql = "SELECT COUNT(*) as cnt FROM {table} WHERE {where}".format(
                table=table, where=where)

            if not prepared:
                cursor.execute(sql)
            else:
                cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return cursor.fetchone().get('cnt')

    def fetch_rows(self, table, fields=None, condition=None, order=None, limit=None, fetchone=False):
        """
        mysql select() function
        Use sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []

            if not fields:
                fields = '*'
            elif isinstance(fields, tuple) or isinstance(fields, list):
                fields = '`{0}`'.format('`, `'.join(fields))
            else:
                fields = fields

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            if not order:
                orderby = ''
            else:
                orderby = 'ORDER BY {order}'.format(order=order)

            limits = "LIMIT {limit}".format(limit=limit) if limit else ""

            sql = "SELECT {fields} FROM {table} WHERE {where} {orderby} {limits}".format(
                fields=fields, table=table, where=where, orderby=orderby, limits=limits)

            if not prepared:
                cursor.execute(sql)
            else:
                cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return cursor.fetchone() if fetchone else cursor.fetchall()

    def get(self, sql, *parameters, **kwparameters):
        """查询sql获取单行记录"""
        with self.connection.cursor() as cursor:
            cursor.execute(sql, kwparameters or parameters)
            self.connection.commit()
            return cursor.fetchone()

    def execute(self, sql, *parameters, **kwparameters):
        """执行给定的查询，从查询返回lastrowid"""
        with self.connection.cursor() as cursor:

            cursor.execute(sql, kwparameters or parameters)
            self.connection.commit()
            return cursor.lastrowid

    def query(self, sql, *parameters, **kwparameters):
        """execute custom sql query"""
        with self.connection.cursor() as cursor:

            cursor.execute(sql, kwparameters or parameters or None)
            self.connection.commit()
            return cursor.fetchall()

    def fetchone(self, table, fields=None, condition=None, order=None, limit=None):
        return self.fetch_rows(table, fields, condition, order, limit, True)

    def join_field_value(self, data, glue=', '):
        sql = comma = ''
        for key in data.keys():
            sql += "{}`{}` = %s".format(comma, key)
            comma = glue
        return sql

    def close(self):
        if getattr(self, 'connection', 0):
            return self.connection.close()

    def __del__(self):
        """close mysql database connection"""
        self.close()
