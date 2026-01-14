# database.py Module Documentation

## Overview

The `database.py` module provides database connectivity and a generic Repository pattern implementation for SQLAlchemy-based database operations. It includes pre-configured SQLite database connections and a type-safe `Repository` class for common CRUD operations.

## Module Contents

### Database Configuration

#### Global Variables

- **`rootdir`**: `str = "."`
  - Root directory for database files
  
- **`cMenu_dbName`**: `str`
  - SQLite database filename path: `{rootdir}\cMenudb.sqlite`

- **`cMenu_engine`**: `sqlalchemy.engine.Engine`
  - Pre-configured SQLAlchemy engine for the cMenu SQLite database
  - Connection string: `sqlite:///{cMenu_dbName}`

- **`_cMenu_Session`**: `sessionmaker`
  - Private session factory for cMenu database connections
  - Created using `sessionmaker(cMenu_engine)`

### Functions

#### `get_cMenu_session()`

Returns a new SQLAlchemy session instance for the cMenu database.

**Returns:**
- `Session`: A new session object bound to the cMenu database

**Example:**
```python
session = get_cMenu_session()
try:
    # Perform database operations
    result = session.query(MyModel).all()
finally:
    session.close()
```

#### `get_cMenu_sessionmaker()`

Returns the session factory (sessionmaker) for the cMenu database.

**Returns:**
- `sessionmaker`: The sessionmaker instance that can be called to create new sessions

**Example:**
```python
SessionFactory = get_cMenu_sessionmaker()
with SessionFactory() as session:
    # Perform database operations
    pass
```

---
<div style="page-break-after: always;"></div>
## Repository Class

### `Repository[T]`

A generic repository class implementing the Repository pattern for database CRUD operations. Uses SQLAlchemy for ORM functionality and provides type-safe operations through Python generics.

**Type Parameters:**
- `T`: The SQLAlchemy model/entity type this repository manages

**Constructor:**

```python
Repository(session_factory, model: Type[T])
```

**Parameters:**
- `session_factory`: A callable that returns a SQLAlchemy session (typically a `sessionmaker`)
- `model`: The SQLAlchemy ORM model class

**Example:**
```python
from calvincTools.models import MenuItem
from calvincTools.database import get_cMenu_sessionmaker, Repository

menu_repo = Repository(get_cMenu_sessionmaker(), MenuItem)
```

---

### Methods

#### `get_all(whereclause=None, order_by=None) -> list[T]`

Retrieve all records matching the given criteria.

**Parameters:**
- `whereclause` (optional): SQLAlchemy WHERE clause expression for filtering
- `order_by` (optional): Column(s) or ORM attribute(s) for ordering
  - Can be a single column or a list/tuple of columns

**Returns:**
- `list[T]`: List of ORM model instances (detached from session)

**Example:**
```python
# Get all records
all_items = menu_repo.get_all()

# Get filtered records
from sqlalchemy import and_
active_items = menu_repo.get_all(
    whereclause=MenuItem.is_active == True
)

# Get filtered and ordered records
sorted_items = menu_repo.get_all(
    whereclause=MenuItem.category == "main",
    order_by=MenuItem.name
)

# Multiple order columns
multi_sorted = menu_repo.get_all(
    order_by=[MenuItem.category, MenuItem.name.desc()]
)
```

**Notes:**
- All returned objects are expunged from the session (detached)
- Session is automatically managed with context manager

---

#### `get_by_id(id_: int, newifnotfound: bool = False) -> T | None`

Retrieve a single record by its primary key ID.

**Parameters:**
- `id_`: The primary key value to look up
- `newifnotfound`: If `True`, returns a new instance with the given ID if not found; if `False`, returns `None`

**Returns:**
- `T | None`: The model instance (detached) or `None` if not found (when `newifnotfound=False`)

**Example:**
```python
# Get existing record
item = menu_repo.get_by_id(42)
if item:
    print(f"Found: {item.name}")
else:
    print("Not found")

# Get existing or create new instance
item = menu_repo.get_by_id(42, newifnotfound=True)
# item is always a MenuItem instance
```

**Notes:**
- Returned object is expunged from the session
- When `newifnotfound=True`, a new instance is created but NOT persisted to the database

---

#### `add(entity: T) -> T`

Add a new entity to the database.

**Parameters:**
- `entity`: The model instance to add

**Returns:**
- `T`: The persisted entity with updated attributes (e.g., auto-generated ID)

**Example:**
```python
new_item = MenuItem(name="New Item", category="main")
saved_item = menu_repo.add(new_item)
print(f"Saved with ID: {saved_item.id}")
```

**Notes:**
- Automatically commits the transaction
- Object is refreshed to get database-generated values
- Returned object is expunged from the session

---

#### `remove(entity: T) -> None`

Delete an entity from the database.

**Parameters:**
- `entity`: The model instance to delete

**Returns:**
- `None`

**Example:**
```python
item = menu_repo.get_by_id(42)
if item:
    menu_repo.remove(item)
    print("Item deleted")
```

**Notes:**
- Automatically commits the transaction
- Handles detached entities by merging them back to the session

---

#### `removewhere(whereclause) -> int`

Delete multiple records matching a WHERE clause.

**Parameters:**
- `whereclause`: SQLAlchemy WHERE clause expression

**Returns:**
- `int`: Number of rows deleted

**Example:**
```python
# Delete all inactive items
deleted_count = menu_repo.removewhere(MenuItem.is_active == False)
print(f"Deleted {deleted_count} items")

# Delete with complex condition
from sqlalchemy import and_
deleted_count = menu_repo.removewhere(
    and_(
        MenuItem.category == "temp",
        MenuItem.created_date < some_date
    )
)
```

**Notes:**
- Automatically commits the transaction
- More efficient than loading and deleting individual entities

---

#### `update(entity: T) -> T`

Update an existing entity in the database.

**Parameters:**
- `entity`: The model instance with updated values

**Returns:**
- `T`: The updated entity (detached)

**Example:**
```python
item = menu_repo.get_by_id(42)
if item:
    item.name = "Updated Name"
    item.is_active = False
    updated_item = menu_repo.update(item)
    print("Item updated")
```

**Notes:**
- Automatically commits the transaction
- Handles detached entities by merging them back to the session
- Returned object is expunged from the session

---

#### `updatewhere(whereclause, values: dict) -> int`

Update multiple records matching a WHERE clause.

**Parameters:**
- `whereclause`: SQLAlchemy WHERE clause expression
- `values`: Dictionary of column names and new values

**Returns:**
- `int`: Number of rows updated

**Example:**
```python
# Update all items in a category
updated_count = menu_repo.updatewhere(
    MenuItem.category == "old_category",
    {"category": "new_category", "updated_at": datetime.now()}
)
print(f"Updated {updated_count} items")

# Bulk activate items
updated_count = menu_repo.updatewhere(
    MenuItem.id.in_([1, 2, 3, 4, 5]),
    {"is_active": True}
)
```

**Notes:**
- Automatically commits the transaction
- More efficient than loading and updating individual entities
- Dictionary keys must match model column names

---

## Usage Patterns

### Basic CRUD Operations

```python
from calvincTools.database import Repository, get_cMenu_sessionmaker
from calvincTools.models import MenuItem

# Initialize repository
repo = Repository(get_cMenu_sessionmaker(), MenuItem)

# CREATE
new_item = MenuItem(name="Coffee", price=3.50)
saved_item = repo.add(new_item)

# READ
item = repo.get_by_id(saved_item.id)
all_items = repo.get_all()

# UPDATE
item.price = 4.00
repo.update(item)

# DELETE
repo.remove(item)
```

### Advanced Queries

```python
from sqlalchemy import and_, or_

# Filtered query
active_items = repo.get_all(
    whereclause=MenuItem.is_active == True,
    order_by=MenuItem.name
)

# Complex filter
results = repo.get_all(
    whereclause=and_(
        MenuItem.category.in_(["drinks", "food"]),
        MenuItem.price < 10.00,
        or_(
            MenuItem.is_featured == True,
            MenuItem.is_special == True
        )
    ),
    order_by=[MenuItem.category, MenuItem.price.desc()]
)
```

### Bulk Operations

```python
# Bulk update
count = repo.updatewhere(
    MenuItem.category == "seasonal",
    {"is_active": False, "notes": "End of season"}
)

# Bulk delete
count = repo.removewhere(
    and_(
        MenuItem.is_active == False,
        MenuItem.created_date < cutoff_date
    )
)
```

---

## Design Patterns

### Repository Pattern

The `Repository` class implements the Repository pattern, which:
- Abstracts data access logic
- Provides a collection-like interface for domain objects
- Centralizes data access code
- Makes unit testing easier by allowing mock repositories

### Session Management

All repository methods use context managers for automatic session management:
- Sessions are created and closed automatically
- Transactions are committed on success
- Objects are detached before returning (safe to use after session closes)

### Type Safety

The generic `Repository[T]` class provides type hints for better IDE support and type checking:
```python
repo: Repository[MenuItem] = Repository(session_factory, MenuItem)
items: list[MenuItem] = repo.get_all()  # Type checker knows this returns MenuItem objects
```

---

## Dependencies

- **SQLAlchemy**: ORM and database toolkit
  - `create_engine`: Database engine creation
  - `sessionmaker`: Session factory
  - `select`, `insert`, `update`, `delete`: SQL operations
  
- **typing**: Type hints and generics
  - `Generic`, `TypeVar`, `Type`, `Sequence`

---

## Notes

- All repository methods automatically manage sessions (open/close/commit)
- Returned objects are detached from sessions (safe to use outside session scope)
- Detached objects can be updated and re-persisted using `update()`
- The module provides a pre-configured setup for the cMenu SQLite database
- Custom databases can use the `Repository` class with their own session factories

---

## See Also

- [SQLAlcTools_doc.md](SQLAlcTools_doc.md) - Additional SQLAlchemy utilities
- [models.py](../models.py) - ORM model definitions
- SQLAlchemy documentation: https://docs.sqlalchemy.org/
