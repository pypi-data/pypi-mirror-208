"""
"""
from enum import Enum
from typing import Iterable, List, Tuple, TYPE_CHECKING, TypeVar

from inflection import tableize

from .constants import *
from .column import Column
from .results import Rows
from .table import Table


if TYPE_CHECKING: from supersql import Supersql  # pragma: no cover


T = TypeVar('T')


class Query():
    def __init__(self, engine: 'Supersql'):
        self._engine = engine
        self._sql = []
        self._args = []
        self._vals = []
        self._zero = None

    def __str__(self) -> str:
        sql = ' '.join(s() for s in self._sql)
        return sql
    
    def _clone(self):
        this = Query(self._engine)
        this._sql = [s for s in self._sql]
        this._args = [a for a in self._args]
        return this

    def _conditional(self, condition: Column, param: any, command: str):
        if(isinstance(condition, str)):
            if not param:
                raise ValueError('''
                    To prevent SQL Injection please use parameterized query with string
                    or use Supersql <type, 'Column'> syntax.
                ''')
        elif not isinstance(condition, Column):
            raise ValueError(f'''
                Supersql {command} command only accepts <type, 'Column'> or a parameterized
                string and param second argument.
            ''')

        if isinstance(condition, str):
            self._args.append(Column.QUOTE(param))
        else:
            self._args.append(condition._arg)

        this = self._clone()
        def _():
            # NOTE: self inside here is self of original query i.e. complete closure every time it is called it appends again
            if isinstance(condition, str):
                # this._args.append(Column.QUOTE(param))
                sql = f'{command} {condition}'
            else:
                # this._args.append(condition._arg)
                arguments = len(this._args)
                vendor = this._engine._vendor
                if vendor == POSTGRES: placeholder = f'${arguments}'
                else: placeholder = '?'
                column_sql = condition._sql.replace('--?--', placeholder)
                sql = f'''{command} {column_sql}'''
            return sql
        self._sql.append(_)
        return self

    async def go(self, Model : T = None) -> Iterable[T]:
        sql = ' '.join(s() for s in self._sql)
        zero = self._zero
        pooled = self._engine._pooled
        ispg = self._engine.vendor == POSTGRES
        connexion = self._engine._connexion

        async def go(conn):
            if zero == SELECT:
                if ispg: results = await conn.fetch(sql, *self._args)
                else:
                    results = await conn.execute_fetchall(sql, self._args)
                return Rows(results, Model)

            if len(self._vals) > 1:
                results = await conn.executemany(sql, tuple(self._vals))
                print('these are the results: ', results, sql)
            else:
                results = await conn.execute(sql, *self._args)
            return Rows(results or [], Model)

        if ispg:
            if pooled:
                async with connexion.acquire() as connection:
                    return await go(connection)
            return await go(connexion)
        else: return await go(connexion) # sqlite then until more databaseas added

    def _limit_offset(self, value: int, command: str):
        if not isinstance(value, int):
            raise ValueError(f'{command} only accepts integer values')
        self._sql.append(lambda : f'''{command} {value}''')
        return self

    def sql(self, unsafe = False) -> str:
        vendor = self._engine.vendor
        sql = str(self._clone())
        if unsafe:
            if vendor != POSTGRES:
                for arg in self._args:
                    sql = sql.replace('?', arg, 1)
            else:
                for pos, arg in enumerate(self._args):
                    sql = sql.replace(f'${pos + 1}', arg, 1)
        return sql

    def AND(self, condition: Column | str, param = None):
        return self._conditional(condition, param, AND)

    def ASC(self):
        def _():
            return f'ASC'
        self._sql.append(_)
        return self
    
    def CREATE(self, artifact: Table | Enum):
        if isinstance(artifact, Table):
            table = artifact.__table__ or artifact.__class__.__name__
            self._sql.append(lambda: f'CREATE TABLE {tableize(table)}')
        if isinstance(artifact, Enum):
            # create type snake_case(artifiact) as enum ()
            pass
        return self

    def DESC(self):
        def _():
            return f'DESC'
        self._sql.append(_)
        return self

    def DELETE(self):
        self._sql.append(lambda : 'DELETE')
        return self

    def FROM(self, *tables: List[str | int]):
        def _():
            _tables = [Table.COERCE(t) for t in tables]
            return f'''FROM {', '.join(_tables)}'''
        self._sql.append(_)
        return self

    def IN(self, *options):
        arguments = len(self._args)
        self._args.extend(options)
        self._sql.append(lambda: f'''IN ({', '.join([f'${arguments + index + 1}' for index, _ in enumerate(options)])})''')
        return self

    def INTO(self, table: Table):
        try: self._sql[-2]
        except: self._sql.append(lambda : f'INTO {table}')
        else: self._sql[-2] = lambda : f'INSERT INTO {table}'
        return self

    def INSERT(self, *columns: Column):
        self._zero = self._zero or INSERT
        def _():
            return f'''({', '.join(str(column) for column in columns)})'''
        self._sql.extend([lambda : '--', _])
        return self

    def INSERT_INTO(self, table: Table, columns: List[Column]):
        self._zero = self._zero or INSERT
        def _():
            return f'''INSERT INTO {table} ({', '.join(str(column) for column in columns)})'''
        self._sql.append(_)
        return self

    def JOIN(self, *tables: Table):
        for table in tables:...
        return self

    def LIMIT(self, limit: int):
        return self._limit_offset(limit, LIMIT)

    def OFFSET(self, offset: int):
        return self._limit_offset(offset, OFFSET)

    def OR(self, condition: Column | str, param = None):
        return self._conditional(condition, param, OR)

    def ORDER_BY(self, column: Column):
        def _():
            return f'''ORDER BY {column._sql or column}'''
        self._sql.append(_)
        return self

    def RAW(self, statement: str):
        self._sql.append(lambda: statement)
        return self

    def RETURNING(self, column: Column):
        def _():
            return f'RETURNING {column}'
        self._sql.append(_)
        return self

    def SELECT(self, *columns) -> 'Query':
        """Pythonic interface to SQL SELECT allowing python
        to be used to build SQL queries.

        Parameters:
            columns (List[str | int]): Variable args param that accepts either a string of
            Supersql Column Type.
            Raises an error if a type other than str | Column is used.
        """
        self._zero = self._zero or SELECT
        def _():
            _columns = [Column.COERCE(f) for f in columns]
            return f'''SELECT {', '.join(_columns)}''' if _columns else 'SELECT *'
        self._sql.append(_)
        return self

    def SET(self, **kwargs):
        statements = []
        vendor = self._engine._vendor
        for column in kwargs:
            arg = Column.QUOTE(kwargs.get(column))
            self._args.append(arg)
            if vendor == POSTGRES: placeholder = f'${len(self._args)}'
            else: placeholder = '?'
            statements.append(f'{column} = {placeholder}')

        def _():
            return f"SET {', '.join(statements)}"
        self._sql.append(_)
        return self

    def UPDATE(self, table: Table):
        self._zero = self._zero or UPDATE
        self._sql.append(lambda : f'''UPDATE {table}''')
        return self

    def VALUES(self, *matrix: Tuple[any]):
        msg = 'VALUES expects a tuple if inserting a row or multiple tuples if inserting multiple rows'
        homogeneous = set()
        for values in matrix:
            if not isinstance(values, (tuple, list)):
                raise ValueError(msg)
            homogeneous.add(len(values))
        if len(homogeneous) > 1:
            raise SyntaxError('VALUES matrix has tuples of different lengths')
        def _():
            vendor = self._engine._vendor
            count = homogeneous.copy().pop()
            if vendor == POSTGRES:
                placeholders = [f'${pos + 1}' for pos in range(count)]
            else:
                placeholders = ['?'] * count
            self._vals.extend(matrix)
            return f'''VALUES ({', '.join(placeholders)})'''
        self._sql.append(_)
        return self

    def WHERE(self, condition: Column | str, param = None):
        # early exit if condition used without an op i.e. ==, AS, etc
        if isinstance(condition, Column) and condition._sql is None:
            self._sql.append(lambda: f'''WHERE {condition}''')
            return self
        return self._conditional(condition, param, WHERE)
