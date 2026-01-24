from typing import (List, Type, Any, )

from sqlalchemy import (FromClause, Table, Select, select, text, inspect, )
from sqlalchemy.orm import (Session, sessionmaker, DeclarativeMeta, )
from sqlalchemy.sql.elements import ClauseElement

# from ..database import (get_cMenu_session, get_cMenu_sessionmaker, )
# from app.database import (get_app_session, get_app_sessionmaker, )


retListofQSQLRecord = -1
retListofSQLRecord = retListofQSQLRecord


def recordsetList(
    # tbl:Table|FromClause,     # _FromClauseArgument ???
    tbl, 
    db,
    retFlds:int|List[str] = retListofQSQLRecord, 
    where:str|None = None, 
    orderby:str|None = None, 
    # ssnmaker: sessionmaker[Session] = get_app_sessionmaker(),
    ) -> List:
    """Execute a SELECT query and return a list of record mappings.
    
    Args:
        tbl (Table | FromClause): The table or query object to select from.
        retFlds (int | List[str], optional): Fields to return. Can be a list of field names,
            '*' for all fields, or retListofQSQLRecord constant. Defaults to retListofQSQLRecord.
        filter (str | None, optional): WHERE clause filter as a string. Defaults to None.
        ssnmaker (sessionmaker[Session], optional): Session maker for database connection.
            Defaults to cMenu_Session.
    
    Returns:
        List: List of record mappings (dictionaries) with the query results.
    """
    if retFlds == '*' or (isinstance(retFlds,List) and retFlds[0]=='*') or retFlds == retListofQSQLRecord:
        stmt = select('*')
    elif isinstance(retFlds, List):
        # Get a set of all valid column-mapped attribute names
        valid_orm_cols = set(c.key for c in inspect(tbl).mapper.column_attrs)

        stmt = select(*[
            getattr(tbl, col) 
            for col in retFlds 
            if col in valid_orm_cols
            ])
    else:
        stmt = select('*')
    #endif retFlds
    stmt = stmt.select_from(tbl)
    if where:
        stmt = stmt.where(text(where))
    #endif filter
    if orderby:
        stmt = stmt.order_by(text(orderby))
    #endif filter

    records = db.session.execute(stmt)
    retList = list(records.mappings())

    return retList
#enddef recordsetList

def get_table_object(obj: DeclarativeMeta | Table | FromClause) -> Table:
    """
    Return the underlying Table object for either:
    - an ORM model class (DeclarativeMeta)
    - a Core Table instance
    """
    if isinstance(obj, DeclarativeMeta):
        return obj.__table__ # type: ignore
    elif isinstance(obj, Table):
        return obj
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")

def select_with_join_excluding(
    left: Table | FromClause, 
    right:  Table | FromClause, 
    on_clause,
    exclude_from_right: List[str]|None = None
) -> Select:
    """
    Select all columns from 'left' table and all columns from 'right' table,
    excluding the specified columns from the right table.
    
    :param left: ORM model or Table for the left side
    :param right: ORM model or Table for the right side
    :param on_clause: join condition
    :param exclude_from_right: list of column names to exclude from right table
    :return: SQLAlchemy Select object
    """
    exclude_from_right_set = set(exclude_from_right or [])
    
    left_tbl = get_table_object(left)
    right_tbl = get_table_object(right)

    left_cols = list(left_tbl.columns)
    right_cols = [
        col for col in right_tbl.columns
        if col.name not in exclude_from_right_set
    ]
    
    stmt = select(*left_cols, *right_cols).join(right_tbl, on_clause)
    return stmt


def select_join_auto_exclude(
    tables: List[Table | FromClause],
    on_clauses: List[object],
    exclude: List[str]|None = None
):
    """
    Build a SELECT that joins multiple tables and automatically removes duplicate column names.
    Optionally exclude specific column names from *all* tables.

    :param tables: List of ORM models or Table objects [T1, T2, T3...]
    :param on_clauses: List of join conditions [T1→T2, T2→T3...]
    :param exclude: List of column names to exclude from *all* tables
    :return: SQLAlchemy Select object
    """
    exclude_set: set[str] = set(exclude or [])
    seen_names:set[str] = set()
    col_list = []

    tbl_objs = [get_table_object(tbl) for tbl in tables]
    for tbl in tbl_objs:
        for col in tbl.columns:
            if col.name not in exclude_set and col.name not in seen_names:
                col_list.append(col)
                seen_names.add(col.name)

    for clause in on_clauses:
        if not isinstance(clause, ClauseElement):
            raise TypeError(f"Join condition {clause} must be a SQL expression, got {type(clause)}")

    # Start with first table and join others in sequence
    stmt = select(*col_list)
    for tbl, clause in zip(tbl_objs[1:], on_clauses):
        stmt = stmt.join(tbl, clause) # type: ignore

    return stmt
#enddef select_join_auto_exclude

def get_primary_key_column(model: Type[Any]) -> Any:
    """Return the single-column primary key for a model."""
    mapper = inspect(model)
    pks = mapper.primary_key
    if len(pks) != 1:
        raise ValueError(f"{model.__name__} must have exactly one primary key")
    return pks[0]
#enddef get_primary_key_column
