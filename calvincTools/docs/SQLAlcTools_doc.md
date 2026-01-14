# SQLAlcTools.py Module Summary

## Overview
This module provides utility functions for working with SQLAlchemy database queries. It simplifies common database operations such as executing SELECT queries, joining tables, and handling column selection with automatic deduplication and exclusion capabilities.

## Dependencies
- **SQLAlchemy**: Core SQL operations (Table, Select, Session, etc.)
- **cMenu.database**: Provides `cMenu_Session` sessionmaker
- **app.database**: Provides `app_Session` sessionmaker

## Public Functions

### `recordsetList(tbl, retFlds=retListofQSQLRecord, filter=None, ssnmaker=cMenu_Session)`
Executes a SELECT query and returns results as a list of record mappings (dictionaries).

**Parameters:**
- `tbl` (Table | FromClause): Table or query object to select from
- `retFlds` (int | List[str]): Fields to return; can be a list of field names, '*' for all fields, or the retListofQSQLRecord constant
- `filter` (str | None): Optional WHERE clause filter as a string
- `ssnmaker` (sessionmaker[Session]): Session maker for database connection (defaults to cMenu_Session)

**Returns:** List of record mappings

### `get_table_object(obj)`
Extracts the underlying Table object from either an ORM model class (DeclarativeMeta) or a Core Table instance.

**Parameters:**
- `obj` (DeclarativeMeta | Table | FromClause): ORM model or Table object

**Returns:** Table object

**Raises:** TypeError if unsupported type is provided

### `select_with_join_excluding(left, right, on_clause, exclude_from_right=None)`
Creates a SELECT statement joining two tables while excluding specified columns from the right table.

**Parameters:**
- `left` (Table | FromClause): Left side table/model
- `right` (Table | FromClause): Right side table/model
- `on_clause`: Join condition
- `exclude_from_right` (List[str] | None): Column names to exclude from right table

**Returns:** SQLAlchemy Select object

### `select_join_auto_exclude(tables, on_clauses, exclude=None)`
Builds a SELECT statement that joins multiple tables with automatic removal of duplicate column names.

**Parameters:**
- `tables` (List[Table | FromClause]): List of tables or ORM models to join
- `on_clauses` (List[object]): List of join conditions matching table pairs
- `exclude` (List[str] | None): Column names to exclude from all tables

**Returns:** SQLAlchemy Select object

**Raises:** TypeError if join conditions are not valid SQL expressions

### `get_primary_key_column(model)`
Retrieves the single-column primary key for a given model.

**Parameters:**
- `model` (Type[Any]): ORM model class

**Returns:** Primary key column object

**Raises:** ValueError if model doesn't have exactly one primary key

## Public Constants

### `retListofQSQLRecord`
Constant value (-1) used to indicate that all fields should be returned in `recordsetList()` function.

### `retListofSQLRecord`
Alias for `retListofQSQLRecord` (also -1).
