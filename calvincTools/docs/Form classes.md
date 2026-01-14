# Form Class Hierarchy

## Overview

This document provides a comprehensive overview of the form class hierarchy in calvincTools. The framework provides specialized classes for building database-backed forms with CRUD operations, supporting both single-record forms and complex nested relationships.

**Module:** `calvincTools.utils.cQdbFormWidgets`

---

## Class Hierarchy Diagram

```
QWidget (PySide6)
│
├── cSimpleTableForm
│   └── Basic table view with add/save (deprecated/limited functionality)
│
├── cSimpRecFmElement_Base (Abstract)
│   │   Base interface for form elements
│   │   • loadFromRecord(rec)
│   │   • saveToRecord(rec)
│   │   • isDirty() / setDirty()
│   │
│   ├── cQFmFldWidg
│   │   └── Standard field widget wrapper (wraps QLineEdit, QComboBox, etc.)
│   │
│   ├── cQFmLookupWidg
│   │   └── Lookup/foreign key field widget with selection handler
│   │
│   ├── cSimpleRecordSubForm1
│   │   └── Table-based subform (one-to-many relationships)
│   │
│   ├── cSimpRecSbFmRecord (cSimpRecFmElement_Base + cSimpleRecordForm_Base)
│   │   └── Single subrecord form element (used within SubForm2)
│   │
│   └── cSimpleRecordSubForm2 (cSimpRecFmElement_Base + cSimpleRecordForm_Base)
│       └── List-based subform with individual record forms
│
└── cSimpleRecordForm_Base (Abstract)
    │   Base class for full-featured record forms
    │   • Database integration (SQLAlchemy ORM)
    │   • Field management (fieldDefs)
    │   • Multi-page/tabbed support
    │   • CRUD operations
    │   • Dirty state tracking
    │   • Navigation (first, previous, next, last)
    │
    └── cSimpleRecordForm
        └── Concrete implementation with standard layout and action buttons
```

---

## Core Classes

### Base/Abstract Classes

#### **cSimpRecFmElement_Base**
- **Purpose:** Abstract base for all form elements (fields, subforms)
- **Parent:** `QWidget`
- **Key Methods:**
  - `loadFromRecord(rec)` - Load data from ORM record
  - `saveToRecord(rec)` - Save data to ORM record
  - `isDirty()` - Check if modified
  - `setDirty(dirty, sendSignal)` - Mark as modified
- **Signals:**
  - `signalFldChanged` - Emitted when value changes
  - `dirtyChanged` - Emitted when dirty state changes

#### **cSimpleRecordForm_Base**
- **Purpose:** Abstract base for full database forms
- **Parent:** `QWidget`
- **Key Attributes:**
  - `_ORMmodel` - SQLAlchemy ORM model class
  - `_primary_key` - Primary key column
  - `_currRec` - Current ORM record (detached)
  - `_ssnmaker` - Database session factory
  - `pages` - List of page/tab names
  - `fieldDefs` - Field definition dictionary
- **Key Methods:**
  - `loadFromRecord(rec)` - Populate form from record
  - `saveToRecord(rec)` - Save form to record
  - `isDirty()` - Check if any field is modified
  - Navigation: `gotoFirstRecord()`, `gotoPrevRecord()`, `gotoNextRecord()`, `gotoLastRecord()`
  - CRUD: `newRecord()`, `saveCurrentRecord()`, `deleteCurrentRecord()`

---

## Field/Element Classes

### **cQFmFldWidg**
- **Purpose:** Standard field widget with label
- **Inherits:** `cSimpRecFmElement_Base`
- **Wraps:** QLineEdit, QComboBox, QCheckBox, QTextEdit, QDateEdit, etc.
- **Features:**
  - Automatic label placement
  - Data binding to ORM fields
  - Dirty tracking
  - Value transformations
- **Usage:** Automatically created by `cSimpleRecordForm_Base` from `fieldDefs`

### **cQFmLookupWidg**
- **Purpose:** Lookup/foreign key field with selection widget
- **Inherits:** `cSimpRecFmElement_Base`
- **Features:**
  - Paired with regular field (e.g., `@CIMSNum` lookup for `CIMSNum` field)
  - Custom selection handlers via `lookupHandler`
  - Supports cDataList, cComboBoxFromDict widgets
- **Usage:** Defined in `fieldDefs` with `@` prefix

---

## Subform Classes

### **cSimpleRecordSubForm1**
- **Purpose:** Table/grid view for one-to-many relationships
- **Inherits:** `cSimpRecFmElement_Base`
- **Display:** QTableView with SQLAlchemyTableModel
- **Best For:** Simple child records (order line items, contact numbers)
- **Features:**
  - Add/Delete buttons
  - Direct cell editing
  - Pending deletion tracking

### **cSimpleRecordSubForm2**
- **Purpose:** List of individual form widgets for one-to-many relationships
- **Inherits:** `cSimpRecFmElement_Base`, `cSimpleRecordForm_Base`
- **Display:** QListWidget with `cSimpRecSbFmRecord` items
- **Best For:** Complex child records requiring detailed forms
- **Features:**
  - Each child record shown as separate form
  - Add/Delete buttons
  - Full form editing per record

### **cSimpRecSbFmRecord**
- **Purpose:** Single subrecord form element (container for one child record)
- **Inherits:** `cSimpRecFmElement_Base`, `cSimpleRecordForm_Base`
- **Usage:** Used within `cSimpleRecordSubForm2`
- **Features:**
  - No navigation buttons (managed by parent)
  - Full field support from `fieldDefs`
  - Dirty tracking integrated with parent form

---

## Form Classes

### **cSimpleRecordForm**
- **Purpose:** Concrete single-record form with full CRUD
- **Inherits:** `cSimpleRecordForm_Base`
- **Features:**
  - Standard layout with header, tabs, and buttons
  - Navigation buttons (first, prev, next, last)
  - Action buttons (new, save, delete, close)
  - Status bar
  - "New Record" indicator
  - Multi-page/tabbed interface
- **Usage:** Subclass and define `_ORMmodel`, `_ssnmaker`, `fieldDefs`, `pages`

### **cSimpleTableForm** (deprecated/limited)
- **Purpose:** Basic table view with minimal editing
- **Inherits:** `QWidget`
- **Features:** Basic add/save functionality
- **Note:** Consider using `cSimpleRecordSubForm1` or more complete alternatives

---

## Inheritance Patterns

### Pattern 1: Standard Form
```python
class MyForm(cSimpleRecordForm):
    _ORMmodel = MyModel
    _ssnmaker = my_session_factory
    _formname = 'My Form'
    pages = ['Main', 'Details']
    fieldDefs = { ... }
```

### Pattern 2: Table Subform
```python
class MySubForm(cSimpleRecordSubForm1):
    _ORMmodel = ChildModel
    _parentFK = 'parent_id'
    _ssnmaker = my_session_factory
```

### Pattern 3: Complex Subform
```python
class MySubForm(cSimpleRecordSubForm2):
    _ORMmodel = ChildModel
    _parentFK = 'parent_id'
    _ssnmaker = my_session_factory
    fieldDefs = { ... }  # Defines layout for each child record
```

---

## Key Design Patterns

### Widget Adapter Pattern
- Qt widgets wrapped in adapter classes (`cQFmFldWidg`, `cQFmLookupWidg`)
- Adapters handle:
  - Data binding to ORM objects
  - Dirty state tracking
  - Value transformations
  - Signal management

### Composition over Deep Inheritance
- `cSimpRecSbFmRecord` and `cSimpleRecordSubForm2` use multiple inheritance
- Combine `cSimpRecFmElement_Base` (element interface) + `cSimpleRecordForm_Base` (form functionality)
- Allows subforms to be both form elements AND full forms

### Detached Record Pattern
- Records loaded from database are detached from session
- Forms work with detached objects
- Changes only persisted when explicitly saved
- Prevents accidental auto-commits

---

## See Also

- [cSimpleRecordForm_Base.md](cSimpleRecordForm_Base.md) - Detailed documentation of base form class
- [cSimpleRecordForm.md](cSimpleRecordForm.md) - Documentation of concrete form implementation
- [Subform_Classes.md](Subform_Classes.md) - Detailed subform documentation
- [fieldDefs dictionary.md](fieldDefs%20dictionary.md) - Field definition specification
