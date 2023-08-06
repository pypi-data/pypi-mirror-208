import logging

from sqlite3 import (
    Cursor as _cur, 
    Connection, 
    ProgrammingError, 
    connect as _connect
)
from typing import Union, Any, Type

def connect(
    database: str, 
    timeout: float = ..., 
    detect_types: int = ..., 
    isolation_level: str | None = ..., 
    check_same_thread: bool = ..., 
    factory: Type[Connection] | None = ..., 
    cached_statements: int = ..., 
    uri: bool = ...
) -> 'fyCursor':

    connection = _connect(
        database=database, 
        timeout=timeout, 
        detect_types=detect_types,
        isolation_level=isolation_level, 
        check_same_thread=check_same_thread,
        factory=factory,
        cached_statements=cached_statements, 
        uri=uri
    )
    return connection.cursor(fyCursor) #type: ignore
    

class fyCursor(_cur):
    """
    Custom `sqlite3.Cursor` that can be used without string query. \n
    I just hate query because it does not have any highlighting, yeah.

    https://github.com/felixyeahh/fyCursor
    """
    def __init__(
        self, 
        __cursor: Connection, 
        logger = None
    ) -> None:
        """
        Initialise a cursor.

        :param __cursor - sqlite3 connection
        :param logger - custom logger (Optional) 
        """
        super().__init__(__cursor)
        self._logger = logging.getLogger("fyCursor") if logger is None else logger
        

    def update(self, table) -> 'fyCursor':
        """
        Use this as SQL `UPDATE {table}` method
        
        :param table: - table to be updated
        :returns: - self
        """
        self._query = f"UPDATE {table}"
        return self


    def add(self, **kwargs) -> 'fyCursor':
        """
        Use this as SQL `SET {kwargs.keys}={kwargs.keys}+{kwargs.values}`
        
        **kwargs

        :returns: - self

        :raises: - `sqlite3.ProgrammingError` if you didn't use `fyCursor.update()` 
        or something similar before this statement
        """
        if not self._query:
            raise ProgrammingError("You should use something before `add`")
        column = list(kwargs.keys())[0]
        value = list(kwargs.values())[0]
        self._query += f" SET {column} = {column} + {value}"
        return self
        

    def set(self, **kwargs) -> 'fyCursor':
        """
        Use this as SQL `SET {kwargs.keys}={kwargs.values}`

        :returns: - self

        :raises: - `sqlite3.ProgrammingError` if you didn't use `fyCursor.update()` 
        or something similar before this statement
        """
        if not self._query:
            raise ProgrammingError("You should use something before `set`")

        column = list(kwargs.keys())[0]
        value = str(list(kwargs.values())[0])
        self._query += f" SET {column} = {value}"
        return self
        

    def select(self, value, from_ = None) -> 'fyCursor':
        """
        Use this as SQL `SELECT {value} FROM {from_}`

        :param value: - value to be selected
        :param from_: - table from which value will be selected

        :returns: - self
        """
        self._query = f"SELECT {value}"
        if from_ is not None:
            self._from(from_)
        return self


    def _from(self, table) -> 'fyCursor':
        self._query += f" FROM {table}"
        return self


    def where(self, **kwargs) -> 'fyCursor':
        if not self._query:
            raise ProgrammingError("You should use something before `where`")
        self._query += f" WHERE {list(kwargs.keys())[0]} = \"{list(kwargs.values())[0]}\""
        return self


    def fetch(self, one: bool = False) -> Union[list, tuple[Any], None]:
        """
        fetch values from cursor query
        
        :param one - if `True` provided, the `cursor.fetchone()` function will be used
        """
        if not self._query:
            raise ProgrammingError("Nothing to fetch")
        super().execute(self._query)
        super().connection.commit()
        return super().fetchone() if one else super().fetchall()        


    def one(self) -> Any:
        """
        returns exact one result of fetching, not tuple
        """
        fetching = self.fetch(True)

        if fetching is None:
            return None
        elif type(fetching) in [list, tuple]:
            return fetching[0]
        return fetching


    def commit(self) -> 'fyCursor':
        if self._query:
            super().execute(self._query)
        super().connection.commit()
        return self