# Subform Classes Documentation

## Overview

The calvincTools framework provides specialized classes for handling one-to-many relationships within database forms. These "subform" classes allow you to embed related child records within a parent record form, with automatic handling of relationships, CRUD operations, and dirty state tracking.

**Module:** `calvincTools.utils.cQdbFormWidgets`

## Three Subform Approaches

The framework offers three distinct approaches to displaying and editing child records:

| Class | Display Style | Best For | Complexity |
|-------|--------------|----------|-----------|
| `cSimpleRecordSubForm1` | Table/Grid View | Simple child records with few fields | Low |
| `cSimpleRecordSubForm2` | Stacked Form Widgets | Complex child records requiring detailed forms | High |
| `cSimpRecSbFmRecord` | Single Record Form | Individual child record within SubForm2 | Medium |

---
<div style="page-break-after: always;"></div>
# cSimpleRecordSubForm1

## Overview

`cSimpleRecordSubForm1` displays related child records in a **table/grid format**, similar to a spreadsheet. This is ideal for simple child records where all fields can be comfortably displayed in columns.

**Parent Classes:** `cSimpRecFmElement_Base`  
**Display Widget:** `QTableView` (customizable)

## Use Cases

- **Order line items**: Product, quantity, price, subtotal
- **Contact phone numbers**: Type, number, primary flag
- **Document attachments**: Filename, size, upload date
- **Transaction history**: Date, amount, type, status
- **Parts list**: Part number, description, quantity

## Key Features

- ✅ Spreadsheet-like table interface
- ✅ Add/Delete buttons for row management
- ✅ Direct cell editing
- ✅ Automatic parent-child relationship management
- ✅ Pending deletion tracking (rows deleted on parent save)
- ✅ Integrates with SQLAlchemyTableModel for database backing

## Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_ORMmodel` | `Type[Any]` | SQLAlchemy ORM model for child records |
| `_primary_key` | `Any` | Primary key of child model (auto-detected) |
| `_parentFK` | `InstrumentedAttribute` | Foreign key linking to parent record |
| `_ssnmaker` | `sessionmaker[Session]` | Database session factory |

## Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_parentRec` | `Any` | Reference to parent record |
| `_parentRecPK` | `Any` | Primary key column of parent record |
| `_childRecs` | `list` | List of child records (detached from session) |
| `_deleted_childRecs` | `list` | List of child records pending deletion |
| `table` | `QTableView` | Table widget displaying child records |
| `Tblmodel` | `SQLAlchemyTableModel` | Data model backing the table |
| `btnAdd` | `QPushButton` | Button to add new rows |
| `btnDel` | `QPushButton` | Button to delete selected rows |

## Constructor

### `__init__(ORMmodel=None, parentFK=None, session_factory=None, viewClass=QTableView, parent=None)`

Initialize a table-based subform.

**Parameters:**
- `ORMmodel` (Type[Any] | None): ORM model class for child records (can be set as class attribute)
- `parentFK` (Any): Foreign key field name (str) or InstrumentedAttribute linking to parent
- `session_factory` (sessionmaker[Session] | None): Database session factory (can be set as class attribute)
- `viewClass` (Type[QTableView]): Table view class to use. Default: QTableView
- `parent` (QWidget | None): Parent widget

**Raises:**
- `ValueError`: If required parameters not provided

**Example:**
```python
class OrderLineSubform(cSimpleRecordSubForm1):
    _ORMmodel = OrderLine
    _parentFK = 'order_id'  # Foreign key field name
    _ssnmaker = SessionMaker

# Or via constructor
subform = cSimpleRecordSubForm1(
    ORMmodel=OrderLine,
    parentFK='order_id',
    session_factory=SessionMaker
)
```

## Methods

### Lifecycle Methods

#### `loadFromRecord(rec)`

Load child records for the given parent record.

**Parameters:**
- `rec`: Parent ORM record instance

**Behavior:**
1. Stores reference to parent record
2. Clears current child record lists
3. Queries database for all child records matching parent FK
4. Detaches child records from session
5. Refreshes table model to display records

**Example:**
```python
# Called automatically by parent form
parent_order = session.get(Order, 123)
subform.loadFromRecord(parent_order)
```

#### `saveToRecord(rec)`

Save child records back to database.

**Parameters:**
- `rec`: Parent ORM record instance

**Behavior:**
1. Validates parent record matches
2. Sets foreign key on all child records
3. Merges new/edited child records to database
4. Deletes records in `_deleted_childRecs` list
5. Commits transaction
6. Clears deleted records list

**Validation:**
- Raises `ValueError` if `rec` doesn't match stored `_parentRec`

**Example:**
```python
# Called automatically by parent form during save
subform.saveToRecord(parent_order)
```

### User Actions

#### `add_row()`

Add a new empty row to the table.

**Behavior:**
1. Creates new instance of child ORM model
2. Sets foreign key to parent's primary key value
3. Inserts row into table model

**Note:** New row is not saved to database until parent form saves.

**Example:**
```python
# Connected to btnAdd.clicked
self.btnAdd.clicked.connect(self.add_row)
```

#### `del_row()`

Delete selected row(s) from the table.

**Behavior:**
1. Gets selected row indices
2. For each selected row (in reverse order):
   - Gets record from table model
   - Removes from `_childRecs` list
   - Adds to `_deleted_childRecs` list
   - Removes row from table model

**Note:** Records are not deleted from database until parent form saves.

**Example:**
```python
# Connected to btnDel.clicked
self.btnDel.clicked.connect(self.del_row)
```

### Adapter Interface (cSimpRecFmElement_Base)

#### `isDirty() -> bool`

Check if any child records have been modified.

**Returns:**
- `True`: If child records added, edited, or deleted
- `False`: If no changes

**Note:** Currently inherits base implementation. Override if custom dirty tracking needed.

#### `setDirty(dirty=True)`

Set dirty state for the subform.

**Parameters:**
- `dirty` (bool): Dirty state to set

**Note:** Currently inherits base implementation. Override if custom dirty tracking needed.

## Complete Usage Example

```python
from PySide6.QtWidgets import QApplication, QLineEdit, QSpinBox
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from calvincTools.utils.cQdbFormWidgets import cSimpleRecordForm, cSimpleRecordSubForm1

# Define ORM models
Base = declarative_base()

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50))
    customer_name = Column(String(100))
    
    # Relationship
    line_items = relationship('OrderLine', back_populates='order')

class OrderLine(Base):
    __tablename__ = 'order_lines'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_name = Column(String(100))
    quantity = Column(Integer)
    unit_price = Column(Float)
    
    # Relationship
    order = relationship('Order', back_populates='line_items')

# Setup database
engine = create_engine('sqlite:///orders.db')
Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)

# Define subform class
class OrderLineSubform(cSimpleRecordSubForm1):
    _ORMmodel = OrderLine
    _parentFK = 'order_id'
    _ssnmaker = SessionMaker

# Define main form
class OrderForm(cSimpleRecordForm):
    _ORMmodel = Order
    _ssnmaker = SessionMaker
    _formname = "Order Editor"
    
    fieldDefs = {
        'order_number': {
            'label': 'Order #',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (0, 0, 1, 1)
        },
        'customer_name': {
            'label': 'Customer',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (1, 0, 1, 2)
        },
        'line_items': {
            'label': 'Line Items',
            'subform_class': OrderLineSubform,
            'page': 0,
            'position': (2, 0, 3, 2)  # Spans multiple rows
        }
    }

# Run application
app = QApplication([])
form = OrderForm()
form.show()
app.exec()
```

## Customization

### Custom Table View

Use a different table view class:

```python
from PySide6.QtWidgets import QTableView

class CustomTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Customize appearance
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)

class MySubform(cSimpleRecordSubForm1):
    _ORMmodel = MyChild
    _parentFK = 'parent_id'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, viewClass=CustomTableView, **kwargs)
```

### Hide Columns

```python
class MySubform(cSimpleRecordSubForm1):
    def loadFromRecord(self, rec):
        super().loadFromRecord(rec)
        # Hide the foreign key column
        fk_col_index = self.Tblmodel.fieldIndex('parent_id')
        self.table.setColumnHidden(fk_col_index, True)
```

### Add Calculated Columns

```python
class OrderLineSubform(cSimpleRecordSubForm1):
    def loadFromRecord(self, rec):
        super().loadFromRecord(rec)
        # Add calculated subtotal column logic here
        # Note: SQLAlchemyTableModel would need extension
```

---
<div style="page-break-after: always;"></div>
# cSimpRecSbFmRecord

## Overview

`cSimpRecSbFmRecord` represents a **single child record in form layout**. This class is used as the building block for `cSimpleRecordSubForm2`, providing a complete form interface for one child record.

**Parent Classes:** `cSimpRecFmElement_Base`, `cSimpleRecordForm_Base`  
**Display Style:** Individual form widget

## Use Cases

- Building block for `cSimpleRecordSubForm2`
- Displaying individual child record in a list
- Complex child records requiring multiple fields and layouts

## Key Features

- ✅ Full form interface for single record
- ✅ Inherits from both adapter and form base classes
- ✅ No navigation buttons (designed for list display)
- ✅ Minimal action buttons (no add/delete)
- ✅ Automatic dirty state tracking
- ✅ Field definitions inherited from parent

## Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_ORMmodel` | `Type[Any]` | ORM model class (from record instance) |
| `_ssnmaker` | `sessionmaker[Session]` | Session factory (from parent widget) |
| `fieldDefs` | `Dict` | Field definitions (from parent widget) |

## Constructor

### `__init__(rec, parent=None)`

Initialize a subrecord form element.

**Parameters:**
- `rec` (Any): ORM record instance to display
- `parent` (QWidget | None): Parent widget (usually cSimpleRecordSubForm2)

**Raises:**
- `ValueError`: If rec doesn't have ORM class
- `ValueError`: If parent doesn't have sessionmaker

**Behavior:**
1. Extracts ORM model from record instance
2. Gets session maker from parent widget
3. Gets field definitions from parent widget
4. Initializes base classes
5. Loads record into form fields

**Example:**
```python
# Typically created by cSimpleRecordSubForm2
record = OrderLine(product='Widget', quantity=5)
form_widget = cSimpRecSbFmRecord(record, parent=subform2_widget)
```

## Methods

### Layout Methods

#### `_buildFormLayout() -> Dict[str, QWidget|QLayout|None]`

Build simplified form layout without header or status bar.

**Returns:**
- Dictionary with layout components (simplified from base class)

**Layout Structure:**
```
┌─────────────────────────────┐
│ Form Fields (in grid)       │
│ ┌─────────┬───────────────┐ │
│ │ Label 1 │ Widget 1      │ │
│ ├─────────┼───────────────┤ │
│ │ Label 2 │ Widget 2      │ │
│ └─────────┴───────────────┘ │
└─────────────────────────────┘
```

#### `_placeFields(layoutFormPages, layoutFormFixedTop, layoutFormFixedBottom, lookupsAllowed=False)`

Place fields into layout (lookups disabled by default).

**Parameters:**
- `layoutFormPages` (QTabWidget): Tab widget (single page)
- `layoutFormFixedTop` (QGridLayout | None): Fixed top section
- `layoutFormFixedBottom` (QGridLayout | None): Fixed bottom section
- `lookupsAllowed` (bool): Whether to create lookup widgets (default: False)

**Note:** Lookups typically disabled since subrecord is part of larger form.

#### `_addActionButtons(layoutButtons)`

No-op implementation (no buttons in subrecord form).

**Note:** Override if buttons needed for specific use case.

#### `_handleActionButton(action)`

No-op implementation (no button actions).

### Display Methods

#### `initialdisplay()`

Override of base class method (does nothing).

**Note:** Record is passed to constructor, so no initial load needed.

### Lifecycle Methods

#### `loadFromRecord(rec)`

Load record data into form fields.

**Parameters:**
- `rec` (object): ORM record instance

**Behavior:**
1. Sets as current record
2. Calls `fillFormFromcurrRec()` to populate fields

#### `saveToRecord(rec)`

Save form field values back to record.

**Parameters:**
- `rec` (object): ORM record instance

**Behavior:**
- Calls parent class `saveToRecord()` implementation
- Collects values from all form widgets
- Updates record attributes

### State Management

#### `setDirty(dirty=True, sendSignal=True)`

Set dirty state and optionally emit signal.

**Parameters:**
- `dirty` (bool): Dirty state to set
- `sendSignal` (bool): Whether to emit `dirtyChanged` signal

## Usage Notes

### Parent Widget Requirements

The parent widget must provide:
- `_ssnmaker`: Database session factory
- `fieldDefs`: Field definition dictionary

### Field Definitions

Field definitions should match the child record's ORM model:

```python
# In cSimpleRecordSubForm2 subclass
fieldDefs = {
    'product_name': {
        'label': 'Product',
        'widgetType': QLineEdit,
        'page': 0,
        'position': (0, 0, 1, 2)
    },
    'quantity': {
        'label': 'Qty',
        'widgetType': QSpinBox,
        'page': 0,
        'position': (1, 0, 1, 1)
    },
    'unit_price': {
        'label': 'Price',
        'widgetType': QLineEdit,
        'page': 0,
        'position': (1, 1, 1, 1)
    }
}
```

---
<div style="page-break-after: always;"></div>
# cSimpleRecordSubForm2

## Overview

`cSimpleRecordSubForm2` displays related child records as **stacked individual form widgets** in a scrollable list. Each child record gets its own complete form interface using `cSimpRecSbFmRecord`. This approach is best for complex child records that require detailed editing.

**Parent Classes:** `cSimpRecFmElement_Base`, `cSimpleRecordForm_Base`  
**Display Widget:** `QListWidget` (customizable)  
**Item Widget:** `cSimpRecSbFmRecord`

## Use Cases

- **Invoice line items with details**: Product selection, pricing tiers, discounts, notes
- **Project tasks**: Task name, description, assigned user, priority, due date, checklist
- **Medical records**: Diagnosis, symptoms, medications, dosage, frequency
- **Curriculum modules**: Module name, description, learning objectives, materials, assessments
- **Equipment maintenance logs**: Date, technician, work performed, parts used, hours

## Key Features

- ✅ Each child record in its own form widget
- ✅ Scrollable list of form widgets
- ✅ Full field layout capabilities per child record
- ✅ Add/Delete buttons for record management
- ✅ Automatic parent-child relationship management
- ✅ Pending deletion tracking
- ✅ Inherits full form capabilities from base classes

## Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_ORMmodel` | `Type[Any]` | SQLAlchemy ORM model for child records |
| `_primary_key` | `Any` | Primary key of child model (auto-detected) |
| `_parentFK` | `InstrumentedAttribute` | Foreign key linking to parent record |
| `_ssnmaker` | `sessionmaker[Session]` | Database session factory |
| `fieldDefs` | `Dict` | Field definitions for child record forms |

## Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_parentRec` | `Any` | Reference to parent record |
| `_parentRecPK` | `Any` | Primary key column of parent record |
| `_childRecs` | `list` | List of child records |
| `_deleted_childRecs` | `list` | List of child records pending deletion |
| `dispArea` | `QListWidget` | List widget containing form widgets |
| `btnAdd` | `QPushButton` | Button to add new records |
| `btnDel` | `QPushButton` | Button to delete selected records |
| `vwClass` | `Type[QListWidget]` | View class used for display area |

## Constructor

### `__init__(ORMmodel=None, parentFK=None, session_factory=None, viewClass=QListWidget, parent=None)`

Initialize a list-based subform.

**Parameters:**
- `ORMmodel` (Type[Any] | None): ORM model class for child records
- `parentFK` (Any): Foreign key field name (str) or InstrumentedAttribute
- `session_factory` (sessionmaker[Session] | None): Database session factory
- `viewClass` (Type[QListWidget]): List widget class. Default: QListWidget
- `parent` (QWidget | None): Parent widget

**Raises:**
- `ValueError`: If required parameters not provided

**Example:**
```python
class TaskSubform(cSimpleRecordSubForm2):
    _ORMmodel = Task
    _parentFK = 'project_id'
    _ssnmaker = SessionMaker
    
    fieldDefs = {
        'task_name': {
            'label': 'Task',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (0, 0, 1, 2)
        },
        'description': {
            'label': 'Description',
            'widgetType': QTextEdit,
            'page': 0,
            'position': (1, 0, 2, 2)
        },
        '@assigned_user_id': {
            'label': 'Assigned To',
            'widgetType': cDataList,
            'page': 0,
            'position': (3, 0, 1, 2)
        }
    }
```

## Methods

### Property Methods

#### `parentFK()` / `setparentFK(pfk)`

Get or set the parent foreign key field.

**Parameters:**
- `pfk` (str | InstrumentedAttribute): Foreign key field

**Raises:**
- `ValueError`: If ORMmodel not set before setting parentFK

#### `parentRec()` / `setparentRec(rec)`

Get or set the parent record.

**Parameters:**
- `rec`: Parent ORM record instance

**Behavior:**
- `setparentRec()` also extracts and stores parent's primary key

#### `parentRecPK()`

Get the parent record's primary key column.

### Layout Methods

#### `_buildFormLayout() -> Dict[str, QWidget|QLayout|None]`

Build the form layout with list widget for child record forms.

**Returns:**
- Dictionary with layout components

**Layout Structure:**
```
┌─────────────────────────────────────┐
│ Scrollable List (dispArea)          │
│ ┌─────────────────────────────────┐ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Child Record Form 1         │ │ │
│ │ └─────────────────────────────┘ │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Child Record Form 2         │ │ │
│ │ └─────────────────────────────┘ │ │
│ │ ┌─────────────────────────────┐ │ │
│ │ │ Child Record Form 3         │ │ │
│ │ └─────────────────────────────┘ │ │
│ └─────────────────────────────────┘ │
├─────────────────────────────────────┤
│ Buttons                             │
│ [Add] [Delete]                      │
└─────────────────────────────────────┘
```

#### `_buildPages(layoutFormPages)`

Override that does nothing (single page only).

#### `_placeFields(layoutFormPages, layoutFormFixedTop, layoutFormFixedBottom, lookupsAllowed=True)`

Override that does nothing (fields handled by `_addDisplayRow`).

#### `_addActionButtons(layoutButtons)`

Add Add and Delete buttons to the subform.

**Buttons:**
- **Add**: Creates new blank child record
- **Delete**: Deletes selected child record forms

### Display Methods

#### `initialdisplay()`

Override that does nothing (no initial display needed).

#### `_addDisplayRow(rec)`

Create and add a form widget for the given record.

**Parameters:**
- `rec`: Child ORM record instance

**Behavior:**
1. Creates `cSimpRecSbFmRecord` widget for record
2. Creates `QListWidgetItem` with appropriate size
3. Adds item to `dispArea`
4. Sets widget as item's widget

**Note:** Does NOT add to `_childRecs` - caller must handle that separately.

**Example:**
```python
# Called internally by loadFromRecord and add_row
new_record = Task(task_name='New Task')
self._childRecs.append(new_record)
self._addDisplayRow(new_record)
```

### CRUD Methods

#### `add_row()`

Add a new child record to the list.

**Behavior:**
1. Creates new instance of child ORM model
2. Sets foreign key to parent's primary key value
3. Appends to `_childRecs` list
4. Calls `_addDisplayRow()` to display

**Example:**
```python
# Connected to btnAdd.clicked
self.btnAdd.clicked.connect(self.add_row)
```

#### `loadFromRecord(rec)`

Load child records for the given parent record.

**Parameters:**
- `rec`: Parent ORM record instance

**Behavior:**
1. Stores reference to parent record and primary key
2. Clears current child record lists
3. Queries database for all child records
4. Detaches child records from session
5. Clears display area
6. Creates form widget for each child record

**Example:**
```python
# Called automatically by parent form
parent_project = session.get(Project, 456)
subform.loadFromRecord(parent_project)
```

#### `saveToRecord(rec)`

Save child records back to database.

**Parameters:**
- `rec`: Parent ORM record instance

**Behavior:**
1. Validates parent record matches
2. Sets foreign key on all child records
3. Merges new/edited child records to database
4. Deletes records in `_deleted_childRecs` list
5. Commits transaction
6. Reloads and refreshes display

**Validation:**
- Raises `ValueError` if `rec` doesn't match stored `_parentRec`

**Example:**
```python
# Called automatically by parent form during save
subform.saveToRecord(parent_project)
```

#### `del_row()`

Delete selected child record(s).

**Status:** Currently incomplete (TODO)

**Intended Behavior:**
1. Get selected items from `dispArea`
2. Extract records from selected form widgets
3. Remove from `_childRecs`
4. Add to `_deleted_childRecs`
5. Remove item from display area

## Complete Usage Example

```python
from PySide6.QtWidgets import (
    QApplication, QLineEdit, QTextEdit, 
    QSpinBox, QDateEdit, QComboBox
)
from sqlalchemy import (
    create_engine, Column, Integer, String, 
    ForeignKey, Date, Text
)
from sqlalchemy.orm import (
    declarative_base, sessionmaker, relationship
)
from calvincTools.utils.cQdbFormWidgets import (
    cSimpleRecordForm, cSimpleRecordSubForm2, cDataList
)

# Define ORM models
Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key=True)
    project_name = Column(String(100))
    description = Column(Text)
    
    # Relationship
    tasks = relationship('Task', back_populates='project')

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    task_name = Column(String(100))
    description = Column(Text)
    assigned_user_id = Column(Integer, ForeignKey('users.id'))
    priority = Column(String(20))
    due_date = Column(Date)
    
    # Relationships
    project = relationship('Project', back_populates='tasks')
    assigned_user = relationship('User')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

# Setup database
engine = create_engine('sqlite:///projects.db')
Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)

# Define subform class with detailed field definitions
class TaskSubform(cSimpleRecordSubForm2):
    _ORMmodel = Task
    _parentFK = 'project_id'
    _ssnmaker = SessionMaker
    
    fieldDefs = {
        'task_name': {
            'label': 'Task Name',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (0, 0, 1, 2),
            'tooltip': 'Enter task name'
        },
        'description': {
            'label': 'Description',
            'widgetType': QTextEdit,
            'page': 0,
            'position': (1, 0, 2, 2),
            'tooltip': 'Detailed task description'
        },
        '@assigned_user_id': {
            'label': 'Assigned To',
            'widgetType': cDataList,
            'page': 0,
            'position': (3, 0, 1, 1),
            'tooltip': 'Select user'
        },
        'priority': {
            'label': 'Priority',
            'widgetType': QComboBox,
            'page': 0,
            'position': (3, 1, 1, 1),
            'choices': ['Low', 'Medium', 'High', 'Critical']
        },
        'due_date': {
            'label': 'Due Date',
            'widgetType': QDateEdit,
            'page': 0,
            'position': (4, 0, 1, 1)
        }
    }

# Define main form
class ProjectForm(cSimpleRecordForm):
    _ORMmodel = Project
    _ssnmaker = SessionMaker
    _formname = "Project Manager"
    
    pages = ['General', 'Tasks']
    
    fieldDefs = {
        'project_name': {
            'label': 'Project Name',
            'widgetType': QLineEdit,
            'page': 'General',
            'position': (0, 0, 1, 2)
        },
        'description': {
            'label': 'Description',
            'widgetType': QTextEdit,
            'page': 'General',
            'position': (1, 0, 3, 2)
        },
        'tasks': {
            'label': 'Tasks',
            'subform_class': TaskSubform,
            'page': 'Tasks',
            'position': (0, 0, 1, 2)
        }
    }

# Run application
app = QApplication([])
form = ProjectForm()
form.show()
app.exec()
```

## Comparison: SubForm1 vs SubForm2

| Feature | SubForm1 (Table) | SubForm2 (Stacked Forms) |
|---------|------------------|--------------------------|
| **Display** | Spreadsheet grid | Stacked form widgets |
| **Best for** | Simple records, few fields | Complex records, many fields |
| **Editing** | In-cell editing | Full form editing |
| **Space efficiency** | High (compact) | Low (expansive) |
| **Field types** | Basic widgets | All widgets including lookups |
| **Visual clarity** | All records visible | One record per widget |
| **Scrolling** | Vertical only | Vertical through forms |
| **Memory usage** | Lower | Higher (one form per record) |
| **Complexity** | Simple | Complex |
| **Lookup support** | Limited | Full support |
| **Layout flexibility** | Column-based | Full grid layout per record |

## Choosing the Right Subform

### Use SubForm1 (Table) when:
- ✅ Child records have 3-7 simple fields
- ✅ All fields fit comfortably in table columns
- ✅ Users are comfortable with spreadsheet-style editing
- ✅ Comparing multiple records visually is important
- ✅ Screen space is limited

### Use SubForm2 (Stacked Forms) when:
- ✅ Child records have many fields (8+)
- ✅ Fields require complex widgets (lookups, dates, text areas)
- ✅ Each record needs dedicated space
- ✅ Users prefer form-based editing
- ✅ Screen space is abundant

## Best Practices

### 1. Field Definitions

Always define `fieldDefs` in SubForm2 class:

```python
class MySubform(cSimpleRecordSubForm2):
    _ORMmodel = MyChild
    _parentFK = 'parent_id'
    
    # Required for cSimpRecSbFmRecord widgets
    fieldDefs = {
        # ... field definitions
    }
```

### 2. Foreign Key Management

Let the subform handle foreign keys automatically:

```python
# Don't include foreign key in fieldDefs
fieldDefs = {
    # 'parent_id': ...  # NO - handled automatically
    'child_field1': {...},
    'child_field2': {...}
}
```

### 3. Save Order

SubForm1 should save before SubForm2 if they reference each other:

```python
# In parent form's fieldDefs, order matters
fieldDefs = {
    'simple_children': {  # Saved first
        'subform_class': SimpleChildSubForm1,
        # ...
    },
    'complex_children': {  # Saved second
        'subform_class': ComplexChildSubForm2,
        # ...
    }
}
```

### 4. Delete Implementation

SubForm2's `del_row()` needs completion:

```python
class MySubform(cSimpleRecordSubForm2):
    def del_row(self):
        """Delete selected child record."""
        selected_items = self.dispArea.selectedItems()
        for item in selected_items:
            # Get the widget
            widget = self.dispArea.itemWidget(item)
            if isinstance(widget, cSimpRecSbFmRecord):
                rec = widget.currRec()
                if rec in self._childRecs:
                    self._childRecs.remove(rec)
                    self._deleted_childRecs.append(rec)
            # Remove from display
            row = self.dispArea.row(item)
            self.dispArea.takeItem(row)
```

### 5. Styling Individual Forms

Customize appearance of child record forms:

```python
class MySubform(cSimpleRecordSubForm2):
    def _addDisplayRow(self, rec):
        """Add styled form widget."""
        wdgt = cSimpRecSbFmRecord(rec, parent=self)
        
        # Add styling
        wdgt.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin: 5px;
                padding: 10px;
            }
        """)
        
        QLWitm = QListWidgetItem()
        QLWitm.setSizeHint(wdgt.sizeHint())
        self.dispArea.addItem(QLWitm)
        self.dispArea.setItemWidget(QLWitm, wdgt)
```

## Troubleshooting

### Issue: Child records not saving
**Cause:** Foreign key not being set correctly  
**Solution:** Verify `_parentFK` matches database column name

### Issue: Forms not displaying in SubForm2
**Cause:** `fieldDefs` not defined  
**Solution:** Define `fieldDefs` as class attribute

### Issue: Deleted records reappear
**Cause:** Delete not fully implemented  
**Solution:** Implement complete `del_row()` method

### Issue: Lookups not working in SubForm2
**Cause:** `lookupsAllowed=False` in `_placeFields`  
**Solution:** Override and set to `True` if needed

## Related Classes

- **cSimpleRecordForm_Base**: Base class providing form functionality
- **cSimpleRecordForm**: Concrete form implementation
- **cSimpRecFmElement_Base**: Base class for form field adapters
- **SQLAlchemyTableModel**: Data model for table-based display

## See Also

- [cSimpleRecordForm_Base.md](./cSimpleRecordForm_Base.md): Base form class documentation
- [cSimpleRecordForm.md](./cSimpleRecordForm.md): Concrete form class documentation
- [database.md](./database.md): Database integration details
- [Form classes.md](./Form%20classes.md): Form class hierarchy overview
