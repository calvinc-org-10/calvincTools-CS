# cSimpleRecordForm_Base Documentation

## Overview

`cSimpleRecordForm_Base` is an abstract base class for creating database-backed forms with CRUD (Create, Read, Update, Delete) operations in PySide6 applications. It provides a comprehensive framework for building single-record forms that interact with SQLAlchemy ORM models.

**Module:** `calvincTools.utils.cQdbFormWidgets`  
**Parent Class:** `QWidget`  
**Type:** Abstract Base Class

## Key Features

- **Database Integration**: Seamless integration with SQLAlchemy ORM models
- **Widget Adapter Pattern**: Automatic wrapping of Qt widgets in adapter classes for data binding
- **Multi-page Support**: Tabbed interface for organizing fields across multiple pages
- **CRUD Operations**: Built-in create, read, update, and delete functionality
- **Dirty State Tracking**: Automatic detection of unsaved changes
- **Lookup Fields**: Special field type for foreign key relationships with selection widgets
- **Subform Support**: Embed complex nested forms within the main form
- **Navigation**: Built-in navigation buttons (first, previous, next, last)
- **Transaction Safety**: Prompts users before discarding unsaved changes

## Architecture

### Design Pattern

The class follows a **Widget Adapter Pattern** where:
- Qt widgets (QLineEdit, QComboBox, etc.) are wrapped in adapter classes
- Adapters (`cSimpRecFmElement_Base`, `cQFmFldWidg`, `cQFmLookupWidg`) handle:
  - Data binding between widgets and ORM objects
  - Dirty state tracking
  - Value transformations

### Workflow

1. **Initialization**: Set up ORM model, session factory, and field definitions
2. **Layout Building**: Create form structure (tabs, layouts, widgets)
3. **Field Placement**: Create and position widgets based on `fieldDefs`
4. **Record Loading**: Fetch record from database, populate form fields
5. **User Interaction**: Track changes, validate input
6. **Persistence**: Save changes back to database with transaction management
7. **Navigation**: Move between records with automatic dirty checking

## Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_ORMmodel` | `Type[Any] \| None` | SQLAlchemy ORM model class backing this form |
| `_primary_key` | `Any` | Primary key column (auto-detected from model) |
| `_currRec` | `Any` | Currently loaded ORM record (detached from session) |
| `_ssnmaker` | `sessionmaker[Session] \| None` | Database session factory for transactions |
| `pages` | `List` | List of page/tab names (empty for single-page forms) |
| `_tabindexTOtabname` | `dict[int, str]` | Maps tab indices to tab names |
| `_tabnameTOtabindex` | `dict[str, int]` | Maps tab names to tab indices |
| `fieldDefs` | `Dict[str, Dict[str, Any]]` | Field definitions (see Field Definition Structure) |

## Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_formWidgets` | `Dict[str, QWidget]` | Maps field names to widget instances |
| `_lookupFrmElements` | `Dict[str, QWidget]` | Maps lookup field names to lookup widgets |
| `layoutFormPages` | `QTabWidget` | Tab widget containing form pages |
| `layoutFormFixedTop` | `QGridLayout \| None` | Fixed section above tabs |
| `layoutFormFixedBottom` | `QGridLayout \| None` | Fixed section below tabs |
| `layoutButtons` | `QBoxLayout` | Layout containing action buttons |
| `_statusBar` | `QStatusBar \| None` | Status bar for messages |
| `_newrecFlag` | `QLabel \| None` | "New Record" indicator label |

## Field Definition Structure

The `fieldDefs` dictionary maps field names to configuration dictionaries. Field names can have special prefixes:
- `@fieldname`: Lookup field (foreign key with selection widget)
- `+fieldname`: Internal variable field (not bound to database)

### Field Configuration Options

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `label` | `str` | Yes | Display label text |
| `widgetType` | `Type[QWidget]` | Yes | Widget class (QLineEdit, QComboBox, etc.) |
| `page` | `int \| str` | Yes | Tab index or name where field appears |
| `position` | `tuple` | Yes | Grid layout position (row, col, [rowspan, colspan]) |
| `align` | `Qt.AlignmentFlag` | No | Label text alignment |
| `choices` | `list \| dict` | No | Options for combo boxes/lists |
| `initval` | `Any` | No | Default value for new records |
| `lookupHandler` | `Callable` | No | Callback for lookup selection events |
| `subform_class` | `Type[cSimpRecFmElement_Base]` | No | Subform widget class |
| `readonly` | `bool` | No | Whether field is read-only |
| `noedit` | `bool` | No | Whether field is non-editable |
| `frame` | `bool` | No | Whether to show widget frame |
| `maximumWidth` | `int` | No | Maximum widget width in pixels |
| `focusPolicy` | `Qt.FocusPolicy` | No | Widget focus policy |
| `tooltip` | `str` | No | Tooltip text |
| `bgColor` | `str` | No | Background color (CSS format) |
| `lblChkBxYesNo` | `str` | No | Label for checkbox yes/no fields |

### Example Field Definitions

```python
fieldDefs = {
    # Standard text field
    'name': {
        'label': 'Full Name',
        'widgetType': QLineEdit,
        'page': 0,
        'position': (0, 0, 1, 2),
        'maximumWidth': 300,
        'tooltip': 'Enter full name'
    },
    
    # Lookup field (foreign key)
    '@category_id': {
        'label': 'Category',
        'widgetType': cDataList,
        'page': 0,
        'position': (1, 0, 1, 2),
        'lookupHandler': lambda data: self.on_category_selected(data)
    },
    
    # Combo box with choices
    'status': {
        'label': 'Status',
        'widgetType': QComboBox,
        'page': 0,
        'position': (2, 0, 1, 1),
        'choices': ['Active', 'Inactive', 'Pending']
    },
    
    # Subform field
    'addresses': {
        'label': 'Addresses',
        'subform_class': AddressSubform,
        'page': 1,
        'position': (0, 0, 1, 2)
    },
    
    # Internal variable field (not in database)
    '+display_total': {
        'label': 'Total',
        'widgetType': QLineEdit,
        'page': 0,
        'position': (3, 0, 1, 1),
        'readonly': True
    }
}
```

## Methods

### Constructor

#### `__init__(model, ssnmaker, parent=None)`

Initialize the base record form.

**Parameters:**
- `model` (Type[Any] | None): ORM model class (can be set as class attribute)
- `ssnmaker` (sessionmaker[Session] | None): Session factory (can be set as class attribute)
- `parent` (QWidget | None): Parent widget

**Raises:**
- `ValueError`: If model or ssnmaker not provided and not set as class attributes

### Abstract Methods (Must Implement)

#### `_buildFormLayout() -> Dict[str, QWidget|QLayout|None]`

Build the main layout, form layout, and button layout.

**Returns:**
Dictionary with required keys:
- `layoutMain`: Main container layout (QVBoxLayout/QHBoxLayout)
- `layoutFormHdr`: Header layout for title and indicators
- `layoutForm`: Main form area container
- `layoutFormPages`: Tab widget for organizing fields
- `layoutButtons`: Layout for action buttons

Optional keys:
- `layoutFormFixedTop`: Fixed section above tabs
- `layoutFormFixedBottom`: Fixed section below tabs
- `statusBar`: Status bar widget
- `newrecFlag`: "New Record" indicator label
- `lblFormName`: Form title label

**Example Implementation:**
```python
def _buildFormLayout(self) -> Dict[str, QWidget|QLayout|None]:
    rtnDict = {}
    
    # Create main structure
    layoutMain = QVBoxLayout(self)
    layoutFormHdr = QHBoxLayout()
    layoutFormPages = QTabWidget()
    layoutButtons = QHBoxLayout()
    
    # Create form title
    lblFormName = cQFmNameLabel(self._formname, self)
    layoutFormHdr.addWidget(lblFormName)
    
    # Create new record indicator
    newrecFlag = QLabel("New Record", self)
    newrecFlag.setStyleSheet("color: red; font-weight: bold;")
    layoutFormHdr.addWidget(newrecFlag)
    
    # Set window title
    self.setWindowTitle(self._formname)
    
    # Build return dictionary
    rtnDict['layoutMain'] = layoutMain
    rtnDict['layoutFormHdr'] = layoutFormHdr
    rtnDict['layoutForm'] = layoutFormPages
    rtnDict['layoutFormPages'] = layoutFormPages
    rtnDict['layoutButtons'] = layoutButtons
    rtnDict['newrecFlag'] = newrecFlag
    rtnDict['lblFormName'] = lblFormName
    
    return rtnDict
```

#### `_addActionButtons(layoutButtons)`

Add action buttons to the form.

**Parameters:**
- `layoutButtons` (QBoxLayout | None): Layout to add buttons to

**Typical Buttons:**
- Navigation: First, Previous, Next, Last
- CRUD: Add, Save, Delete
- Other: Cancel, Close, Refresh

#### `_handleActionButton(action)`

Handle action button clicks.

**Parameters:**
- `action` (str): Action name (e.g., 'save', 'delete', 'first')

### Property Getters/Setters

#### `ORMmodel()` / `setORMmodel(model)`

Get or set the ORM model class.

#### `primary_key()` / `setPrimary_key()`

Get or set the primary key column (auto-detected from model).

#### `ssnmaker()` / `setssnmaker(ssnmaker)`

Get or set the session maker.

#### `currRec()` / `setcurrRec(rec)`

Get or set the current record.

### Layout Methods

#### `_buildPages(layoutFormPages)`

Build tabs for multi-page forms based on `self.pages`.

**Parameters:**
- `layoutFormPages` (QTabWidget): Tab widget to populate

#### `FormPage(idx) -> QGridLayout|None`

Get the QGridLayout for a specific page.

**Parameters:**
- `idx` (int | str): Page index (0-based), page name, or special constant:
  - `cQFmConstants.pageFixedTop.value (-1)`: Returns layoutFormFixedTop
  - `cQFmConstants.pageFixedBottom.value (-2)`: Returns layoutFormFixedBottom

**Returns:**
- QGridLayout for the page, or None if not found

#### `numPages() -> int`

Return the number of pages/tabs in the form.

#### `_placeFields(layoutFormPages, layoutFormFixedTop, layoutFormFixedBottom, lookupsAllowed=True)`

Build widgets and place them in layouts based on `fieldDefs`.

**Parameters:**
- `layoutFormPages` (QTabWidget): Tab widget containing form pages
- `layoutFormFixedTop` (QGridLayout | None): Optional fixed top section
- `layoutFormFixedBottom` (QGridLayout | None): Optional fixed bottom section
- `lookupsAllowed` (bool): Whether to create lookup widgets

#### `_finalizeMainLayout(layoutMain, items)`

Add all sub-layouts to the main layout.

**Parameters:**
- `layoutMain` (QVBoxLayout): Main container layout
- `items` (List | tuple): Layouts/widgets to add in order

### Display Methods

#### `initialdisplay()`

Initialize and display the first record.

#### `fillFormFromcurrRec()`

Load the current record into all form fields.

Called after:
- Loading a record from database
- Creating a new blank record
- Discarding changes

#### `showNewRecordFlag()`

Show or hide the "New Record" flag based on current record state.

#### `showCommitButton()`

Enable/disable the commit button based on dirty state.

#### `showError(message, title="Error")`

Display an error message.

**Parameters:**
- `message` (str): Error message text
- `title` (str): Dialog title

#### `statusBar() -> QStatusBar|None`

Get the status bar widget.

#### `repopLookups()`

Repopulate all lookup widgets (e.g., after a save).

### Navigation Methods

#### `isit_OKToLeaveRecord() -> bool`

Check if it's safe to leave the current record.

Checks for unsaved changes and prompts user if found.

**Returns:**
- `True`: Safe to proceed (saved, discarded, or no changes)
- `False`: User cancelled

**User Options:**
- Yes: Save changes and proceed
- No: Discard changes and proceed
- Cancel: Stay on current record

#### `_navigate_to(rec_id)`

Navigate to a record with automatic dirty checking.

**Parameters:**
- `rec_id` (int): Primary key value of record to load

#### `get_prev_record_id(recID) -> int`

Get the ID of the previous record.

**Parameters:**
- `recID` (int): Current record ID

**Returns:**
- ID of previous record, or None if none exists

#### `get_next_record_id(recID) -> int`

Get the ID of the next record.

**Parameters:**
- `recID` (int): Current record ID

**Returns:**
- ID of next record, or None if none exists

#### `on_loadfirst_clicked()`

Load the first record in the database.

#### `on_loadprev_clicked()`

Load the previous record in the database.

#### `on_loadnext_clicked()`

Load the next record in the database.

#### `on_loadlast_clicked()`

Load the last record in the database.

### CRUD Methods

#### Create

##### `initializeRec(initializeTo=None)`

Initialize a new blank record.

**Parameters:**
- `initializeTo` (Type[Any] | None): Alternative model class to instantiate

**Note:** Subclasses should call `fillFormFromcurrRec()` after setting default values.

##### `on_add_clicked()`

Handle add/new record button click.

Creates a new blank record for data entry. Prompts to save if current record has unsaved changes.

#### Read

##### `_load_record_by_id(pk_val)`

Load a record by primary key value.

**Parameters:**
- `pk_val`: Primary key value to load

**Note:** Low-level method that assumes it's safe to replace current record. Use `_navigate_to()` for safe navigation with dirty checking.

##### `load_record(recindex)`

Load a record from the database.

**Parameters:**
- `recindex` (int): Record ID to load

##### `load_record_by_field(field, value)`

Load a record by searching for a specific field value.

**Parameters:**
- `field` (str | Any): Field name or ORM field object
- `value` (Any): Value to search for

**Example:**
```python
# Load by string field name
self.load_record_by_field('email', 'user@example.com')

# Load by ORM field object
self.load_record_by_field(User.email, 'user@example.com')
```

##### `lookup_and_load(fld, value)`

Load a record via lookup field selection.

**Parameters:**
- `fld` (str): Field name to search
- `value` (Any): Value from lookup widget

#### Update

##### `changeFieldSlot(widget)`

Slot for handling widget change signals.

**Parameters:**
- `widget` (QWidget | None): Widget that triggered the signal

##### `changeField(wdgt, dbField, wdgt_value, force=False)`

Handle field value changes from form widgets.

**Parameters:**
- `wdgt` (QWidget): Widget that changed
- `dbField` (str): Database field name
- `wdgt_value` (Any): New value from widget
- `force` (bool): Currently unused

**Transformation Hooks:**

Subclasses can define transformation methods:
```python
def _transform_email(self, value):
    return value.lower().strip()

def _transform_phone(self, value):
    # Remove non-numeric characters
    return ''.join(c for c in value if c.isdigit())
```

##### `changeInternalVarField(wdgt, intVarField, wdgt_value)`

Handle internal variable field changes.

**Parameters:**
- `wdgt`: Widget that changed
- `intVarField` (str): Internal variable field name
- `wdgt_value` (Any): New value

**Note:** Must be implemented by subclass if internal variable fields are used.

##### `on_save_clicked()`

Save the current record to the database.

**Workflow:**
1. Push data from form widgets to ORM object (except subforms)
2. Merge and commit via short-lived session
3. Save subforms (which may reference the main record)
4. Reload record to get database defaults and new ID

#### Delete

##### `on_delete_clicked()`

Delete the current record.

Prompts for confirmation, deletes record, and navigates to neighboring record.

### State Management

#### `isNewRecord() -> bool`

Check if the current record is new (unsaved).

**Returns:**
- `True`: Record has no primary key value
- `False`: Record exists in database

#### `setDirty(dirty=None)`

Set or poll dirty state for form elements.

**Parameters:**
- `dirty` (bool | None): If bool, propagates to all child widgets. If None, only updates commit button.

#### `isDirty() -> bool`

Check if any form element has been modified.

**Returns:**
- `True`: At least one field is dirty
- `False`: No unsaved changes

## Complete Usage Example

```python
from PySide6.QtWidgets import QApplication, QLineEdit, QComboBox, QTextEdit
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from calvincTools.utils.cQdbFormWidgets import cSimpleRecordForm_Base, cQFmNameLabel

# Define ORM model
Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    status = Column(String(20))
    notes = Column(String)

# Create engine and session factory
engine = create_engine('sqlite:///example.db')
Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)

# Define custom form
class PersonForm(cSimpleRecordForm_Base):
    _ORMmodel = Person
    _ssnmaker = SessionMaker
    _formname = "Person Editor"
    
    pages = ['General', 'Notes']
    
    fieldDefs = {
        'name': {
            'label': 'Full Name',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (0, 0, 1, 2),
            'tooltip': 'Enter full name'
        },
        'email': {
            'label': 'Email',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (1, 0, 1, 2),
            'tooltip': 'Enter email address'
        },
        'status': {
            'label': 'Status',
            'widgetType': QComboBox,
            'page': 0,
            'position': (2, 0, 1, 1),
            'choices': ['Active', 'Inactive', 'Pending']
        },
        'notes': {
            'label': 'Notes',
            'widgetType': QTextEdit,
            'page': 'Notes',
            'position': (0, 0, 1, 2)
        }
    }
    
    def _buildFormLayout(self):
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QStatusBar
        from calvincTools.utils.cQWidgets import cstdTabWidget, cGridWidget
        
        rtnDict = {}
        
        layoutMain = QVBoxLayout(self)
        layoutFormHdr = QHBoxLayout()
        layoutForm = cGridWidget(scrollable=True)
        layoutFormPages = cstdTabWidget()
        layoutButtons = QHBoxLayout()
        statusBar = QStatusBar(self)
        
        lblFormName = cQFmNameLabel(self._formname, self)
        layoutFormHdr.addWidget(lblFormName)
        
        self.setWindowTitle(self._formname)
        
        rtnDict['layoutMain'] = layoutMain
        rtnDict['layoutFormHdr'] = layoutFormHdr
        rtnDict['layoutForm'] = layoutForm
        rtnDict['layoutFormPages'] = layoutFormPages
        rtnDict['layoutButtons'] = layoutButtons
        rtnDict['statusBar'] = statusBar
        
        return rtnDict
    
    def _addActionButtons(self, layoutButtons):
        from PySide6.QtWidgets import QPushButton
        
        btnFirst = QPushButton("First")
        btnFirst.clicked.connect(self.on_loadfirst_clicked)
        layoutButtons.addWidget(btnFirst)
        
        btnPrev = QPushButton("Previous")
        btnPrev.clicked.connect(self.on_loadprev_clicked)
        layoutButtons.addWidget(btnPrev)
        
        btnNext = QPushButton("Next")
        btnNext.clicked.connect(self.on_loadnext_clicked)
        layoutButtons.addWidget(btnNext)
        
        btnLast = QPushButton("Last")
        btnLast.clicked.connect(self.on_loadlast_clicked)
        layoutButtons.addWidget(btnLast)
        
        layoutButtons.addStretch()
        
        btnAdd = QPushButton("Add")
        btnAdd.clicked.connect(self.on_add_clicked)
        layoutButtons.addWidget(btnAdd)
        
        self.btnCommit = QPushButton("Save")
        self.btnCommit.clicked.connect(self.on_save_clicked)
        layoutButtons.addWidget(self.btnCommit)
        
        btnDelete = QPushButton("Delete")
        btnDelete.clicked.connect(self.on_delete_clicked)
        layoutButtons.addWidget(btnDelete)
    
    def _handleActionButton(self, action):
        # Not used in this simple example
        pass
    
    # Optional: Add email transformation
    def _transform_email(self, value):
        return value.lower().strip()

# Run application
if __name__ == '__main__':
    app = QApplication([])
    form = PersonForm()
    form.show()
    app.exec()
```

## Advanced Features

### Transformation Hooks

Define methods named `_transform_{fieldname}` to automatically transform values:

```python
def _transform_phone(self, value):
    """Strip non-numeric characters from phone numbers."""
    return ''.join(c for c in value if c.isdigit())

def _transform_email(self, value):
    """Normalize email addresses."""
    return value.lower().strip()
```

### Lookup Fields

Lookup fields provide a selection widget (dropdown or list) for foreign keys:

```python
'@department_id': {
    'label': 'Department',
    'widgetType': cDataList,
    'page': 0,
    'position': (3, 0, 1, 2),
    'lookupHandler': self.on_department_selected
}

def on_department_selected(self, data):
    """Handle department selection."""
    dept_id = data.get('id') if isinstance(data, dict) else data
    # Perform additional actions based on selection
```

### Subforms

Embed complex nested forms for one-to-many or many-to-many relationships:

```python
'addresses': {
    'label': 'Addresses',
    'subform_class': AddressListSubform,
    'page': 'Contact',
    'position': (0, 0, 1, 2)
}
```

Subform classes must inherit from `cSimpRecFmElement_Base`.

### Internal Variable Fields

Fields that exist in the form but not in the database (for calculations, display, etc.):

```python
'+calculated_total': {
    'label': 'Total',
    'widgetType': QLineEdit,
    'page': 0,
    'position': (4, 0, 1, 1),
    'readonly': True
}
```

Handle updates in `changeInternalVarField()` method.

## Best Practices

1. **Session Management**: Always use short-lived sessions. Never store session objects as instance attributes.

2. **Record Detachment**: Always detach records from sessions using `session.expunge()` before storing in `_currRec`.

3. **Dirty Checking**: Call `isit_OKToLeaveRecord()` before any navigation to prevent data loss.

4. **Field Naming**: Use consistent naming between database columns and field definition keys.

5. **Layout Organization**: Group related fields on the same page/tab.

6. **Error Handling**: Always wrap database operations in try-except blocks.

7. **Button State**: Keep save/commit button disabled when no changes exist.

8. **Validation**: Implement field validation before saving to database.

## Related Classes

- **cSimpleRecordForm**: Concrete implementation with standard layout
- **cSimpRecFmElement_Base**: Base class for form field adapters
- **cQFmFldWidg**: Standard form field widget wrapper
- **cQFmLookupWidg**: Lookup field widget wrapper
- **cQFmNameLabel**: Styled label for form titles
- **cstdTabWidget**: Standard tab widget with enhancements
- **cGridWidget**: Grid widget with optional scrolling

## See Also

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Form classes.md](./Form%20classes.md): Overview of form class hierarchy
- [database.md](./database.md): Database integration details
