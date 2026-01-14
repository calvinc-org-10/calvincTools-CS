# dbmenulist.py Module Summary

## Overview
This module provides database management functionality for menu items in the cMenu system. It defines template menu structures and the `MenuRecords` class for CRUD operations and querying menu data from the database.

## Dependencies
- **SQLAlchemy**: Database ORM and query building
- **menucommand_constants**: Command number constants (COMMANDNUMBER)
- **database**: cMenu_Session sessionmaker
- **utils**: Database utility functions (recordsetList, select_with_join_excluding)
- **models**: menuGroups and menuItems ORM models

## Public Constants/Data

### `initmenu_menulist`
List of dictionaries defining the initial/default menu structure with MenuID = -1. Contains options like:
- New Menu (option 0)
- Edit Menu (option 11)
- Change Password (option 19)
- Go Away!/Exit Application (option 20)

### `newgroupnewmenu_menulist`
List of dictionaries for creating a new menu in a new group with MenuID = 0. Contains:
- New Menu (option 0)
- Change Password (option 19)
- Go Away!/Exit Application (option 20)

### `newmenu_menulist`
List of dictionaries for creating a new menu without MenuID specified. Contains:
- New Menu (option 0)
- Return to Main Menu (option 20)

## Public Classes

### `MenuRecords`
A context manager class for managing menu items in the database with CRUD operations and specialized queries.

**Attributes:**
- `_tbl`: Reference to menuItems model
- `_tblGroup`: Reference to menuGroups model
- `session`: Database session (managed by context manager)

**Methods:**

#### `__init__()`
Initialize the MenuRecords instance.

#### `__enter__()` / `__exit__(exc_type, exc_val, exc_tb)`
Context manager support for automatic session management with commit/rollback.

#### `create(persist=True, **kwargs)`
Creates a new menu item record.

**Parameters:**
- `persist` (bool): Whether to persist to database immediately (default: True)
- `**kwargs`: Field values for the new menu item

**Returns:** menuItems object

#### `get(record_id)`
Retrieves a menu item by its primary key.

**Parameters:**
- `record_id` (int): Primary key of the menu item

**Returns:** menuItems object or None

#### `update(record_id, **kwargs)`
Updates an existing menu item record.

**Parameters:**
- `record_id` (int): Primary key of the menu item to update
- `**kwargs`: Field values to update

**Returns:** Updated menuItems object or None

#### `delete(record_id)`
Deletes a menu item record.

**Parameters:**
- `record_id` (int): Primary key of the menu item to delete

**Returns:** bool (True if deleted, False if not found)

#### `menuAttr(mGroup, mID, Opt, AttrName)`
Gets a specific attribute value from a menu item.

**Parameters:**
- `mGroup` (int): Menu group ID
- `mID` (int): Menu ID
- `Opt` (int): Option number
- `AttrName` (str): Name of the attribute to retrieve

**Returns:** Any - The attribute value

#### `minMenuID_forGroup(mGroup)`
Returns the minimum MenuID for the given MenuGroup.

**Parameters:**
- `mGroup` (int): Menu group ID

**Returns:** int or None - Minimum MenuID

#### `dfltMenuID_forGroup(mGroup)`
Returns the default MenuID for a group (marked with 'default' argument) or falls back to minimum MenuID.

**Parameters:**
- `mGroup` (int): Menu group ID

**Returns:** int or None - Default MenuID

#### `dfltMenuGroup()`
Returns the minimum (default) MenuGroup ID.

**Returns:** int or None - Default menu group ID

#### `menuDict(mGroup, mID)`
Retrieves menu items as a dictionary with OptionNumber as keys.

**Parameters:**
- `mGroup` (int): Menu group ID
- `mID` (int): Menu ID

**Returns:** Dict[int, Dict[str, Any]] - Dictionary mapping option numbers to field dictionaries

#### `menuDBRecs(mGroup, mID)`
Retrieves menu items as a dictionary of menuItems objects.

**Parameters:**
- `mGroup` (int): Menu group ID
- `mID` (int): Menu ID

**Returns:** Dict[int, menuItems] - Dictionary mapping option numbers to menuItems objects

#### `menuExist(mGroup, mID)`
Checks if a menu exists (has option number 0).

**Parameters:**
- `mGroup` (int): Menu group ID
- `mID` (int): Menu ID

**Returns:** bool - True if menu exists, False otherwise

#### `recordsetList(retFlds=retListofQSQLRecord, filter=None)`
Retrieves a list of menu records with joined group information, excluding the 'id' column from groups.

**Parameters:**
- `retFlds` (int | List[str]): Fields to return (default: all fields)
- `filter` (str | None): Optional WHERE clause filter

**Returns:** List[RowMapping] - List of record mappings

#### `newgroupnewmenuDict(mGroup, mID)`
Returns the template menu structure for a new group/new menu.

**Parameters:**
- `mGroup` (int): Menu group ID (not used in current implementation)
- `mID` (int): Menu ID (not used in current implementation)

**Returns:** List[Dict] - newgroupnewmenu_menulist

#### `newmenuDict(mGroup, mID)`
Returns the template menu structure for a new menu.

**Parameters:**
- `mGroup` (int): Menu group ID (not used in current implementation)
- `mID` (int): Menu ID (not used in current implementation)

**Returns:** List[Dict] - newmenu_menulist
