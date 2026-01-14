# cSimpleRecordForm Documentation

## Overview

`cSimpleRecordForm` is a concrete implementation of `cSimpleRecordForm_Base` that provides a complete, ready-to-use single-record form with standard layout, navigation buttons, and CRUD operations. This class is the most commonly used form class for creating database-backed forms with minimal boilerplate code.

**Module:** `calvincTools.utils.cQdbFormWidgets`  
**Parent Class:** `cSimpleRecordForm_Base`  
**Type:** Concrete Class (ready to use or extend)

## Key Features

- **Complete Implementation**: All abstract methods from base class are implemented
- **Standard Layout**: Pre-configured tabbed interface with header, status bar, and button panel
- **Icon-Based Buttons**: Uses QtAwesome icons for professional appearance
- **Navigation Controls**: First, Previous, Next, Last buttons with automatic record traversal
- **CRUD Operations**: Add, Save, Delete, Cancel buttons fully wired
- **Flexible Customization**: Override methods to customize behavior
- **Action Dispatch System**: Centralized button action handling

## What's Different from Base Class

Unlike `cSimpleRecordForm_Base` which is abstract, `cSimpleRecordForm`:

1. ✅ **Implements `_buildFormLayout()`**: Creates standard form structure with header, scrollable tabbed area, button panel, and status bar
2. ✅ **Implements `_addActionButtons()`**: Adds navigation and CRUD buttons with icons
3. ✅ **Implements `_handleActionButton()`**: Dispatches button clicks to appropriate handlers
4. ✅ **Adds `_formname` attribute**: Form title/name management
5. ✅ **Provides `on_cancel_clicked()`**: Cancel button functionality
6. ✅ **Overrides `repopLookups()`**: Properly refreshes lookup widgets

## When to Use

### Use `cSimpleRecordForm` when:
- You need a standard single-record form quickly
- You want navigation and CRUD buttons out-of-the-box
- You're satisfied with the default layout structure
- You want to focus on defining `fieldDefs` rather than layout code

### Use `cSimpleRecordForm_Base` when:
- You need complete control over layout structure
- You want a non-standard button arrangement
- You're building a specialized form type (e.g., wizard, multi-section form)
- You need a custom header or footer layout

### Extend `cSimpleRecordForm` when:
- You want the standard layout but need additional customization
- You need to override specific methods (e.g., save behavior)
- You want to add custom buttons or handlers

## Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `_formname` | `str` | Form title displayed in header and window title |
| `_ORMmodel` | `Type[Any] \| None` | SQLAlchemy ORM model class (inherited) |
| `_ssnmaker` | `sessionmaker[Session] \| None` | Database session factory (inherited) |
| `pages` | `List[str]` | List of page/tab names (inherited) |
| `fieldDefs` | `Dict[str, Dict[str, Any]]` | Field definitions (inherited) |

## Instance Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `dictFormLayouts` | `Dict[str, QWidget|QLayout|None]` | Dictionary returned from _buildFormLayout |

## Constructor

### `__init__(model=None, formname=None, ssnmaker=None, parent=None)`

Initialize the form with standard layout.

**Parameters:**
- `model` (Type[Any] | None): ORM model class (can be set as class attribute)
- `formname` (str | None): Form title/name. If None, uses class attribute `_formname` or defaults to 'Form'
- `ssnmaker` (sessionmaker[Session] | None): Session factory (can be set as class attribute)
- `parent` (QWidget | None): Parent widget

**Example:**
```python
# Using constructor parameters
form = cSimpleRecordForm(
    model=Person,
    formname="Person Editor",
    ssnmaker=my_sessionmaker
)

# Using class attributes
class PersonForm(cSimpleRecordForm):
    _ORMmodel = Person
    _ssnmaker = my_sessionmaker
    _formname = "Person Editor"
    
form = PersonForm()
```

<div style="page-break-after: always;"></div>
## Layout Structure

The standard layout created by `_buildFormLayout()`:

```
┌─────────────────────────────────────────────────────┐
│ Form Header (layoutFormHdr)                        │
│ ┌─────────────────────┐ ┌───────────────┐         │
│ │ Form Title          │ │ "New Record"  │         │
│ └─────────────────────┘ └───────────────┘         │
├─────────────────────────────────────────────────────┤
│ Scrollable Form Area (layoutForm)                  │
│ ┌─────────────────────────────────────────────────┐│
│ │ layoutFormFixedTop (optional)                   ││
│ ├─────────────────────────────────────────────────┤│
│ │ Tab Widget (layoutFormPages)                    ││
│ │ ┌────┬────┬────┐                                ││
│ │ │Tab1│Tab2│Tab3│                                ││
│ │ ├────┴────┴────┴──────────────────────────────┐ ││
│ │ │                                              │ ││
│ │ │  Form fields arranged in grid                │ ││
│ │ │                                              │ ││
│ │ └──────────────────────────────────────────────┘ ││
│ ├─────────────────────────────────────────────────┤│
│ │ layoutFormFixedBottom (optional)                ││
│ └─────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────┤
│ Button Panel (layoutButtons)                       │
│ ┌──────────────────┐  ┌──────────────────────────┐│
│ │ Navigation       │  │ CRUD Actions             ││
│ │ [<<] [<] [>] [>>]│  │ [+] [Save] [Del] [Cancel]││
│ └──────────────────┘  └──────────────────────────┘│
├─────────────────────────────────────────────────────┤
│ Status Bar (statusBar)                             │
│ Ready                                              │
└─────────────────────────────────────────────────────┘
```

### Layout Components

| Component | Type | Description |
|-----------|------|-------------|
| `layoutMain` | `QVBoxLayout` | Root layout containing all other components |
| `layoutFormHdr` | `QHBoxLayout` | Header with form title and new record flag |
| `layoutForm` | `cGridWidget` | Scrollable container for form fields |
| `layoutFormFixedTop` | `QGridLayout` | Optional fixed section above tabs |
| `layoutFormPages` | `cstdTabWidget` | Tab widget for organizing fields |
| `layoutFormFixedBottom` | `QGridLayout` | Optional fixed section below tabs |
| `layoutButtons` | `QHBoxLayout` | Button panel with navigation and CRUD buttons |
| `statusBar` | `QStatusBar` | Status messages and indicators |

## Methods

### Layout Methods

#### `_buildFormLayout() -> Dict[str, QWidget|QLayout|None]`

Creates the standard form layout structure.

**Returns:**
Dictionary containing:
- `layoutMain`: Main vertical layout
- `layoutFormHdr`: Header layout with title and indicators
- `layoutForm`: Scrollable form area wrapper
- `layoutFormFixedTop`: Optional fixed top section
- `layoutFormPages`: Tab widget for pages
- `layoutFormFixedBottom`: Optional fixed bottom section
- `layoutButtons`: Button layout (initially QHBoxLayout)
- `statusBar`: Status bar widget
- `lblFormName`: Form title label
- `newrecFlag`: "New Record" indicator label

**Note:** This method is automatically called by the base class constructor.

### Button Methods

#### `_addActionButtons(layoutButtons=None, layoutHorizontal=True, NavActions=None, CRUDActions=None)`

Add navigation and CRUD buttons with icons.

**Parameters:**
- `layoutButtons` (QBoxLayout | None): Layout to add buttons to (usually self.layoutButtons)
- `layoutHorizontal` (bool): Whether to use horizontal layout. Default: True
- `NavActions` (list[tuple[str, QIcon]] | None): Custom navigation actions. Default: standard navigation
- `CRUDActions` (list[tuple[str, QIcon]] | None): Custom CRUD actions. Default: standard CRUD

**Default Navigation Actions:**
- First: Navigate to first record (mdi.page-first icon)
- Previous: Navigate to previous record (mdi.arrow-left-bold icon)
- Next: Navigate to next record (mdi.arrow-right-bold icon)
- Last: Navigate to last record (mdi.page-last icon)

**Default CRUD Actions:**
- Add: Create new blank record (mdi.plus icon)
- Save: Commit changes to database (mdi.content-save icon)
- Delete: Remove current record (mdi.delete icon)
- Cancel: Close form without saving (mdi.cancel icon)

**Customization Example:**
```python
import qtawesome

class CustomForm(cSimpleRecordForm):
    def _addActionButtons(self, layoutButtons=None, **kwargs):
        # Custom button set
        custom_nav = [
            ("Home", qtawesome.icon("mdi.home")),
            ("End", qtawesome.icon("mdi.arrow-down-bold")),
        ]
        custom_crud = [
            ("New", qtawesome.icon("mdi.file-plus")),
            ("Save", qtawesome.icon("mdi.content-save")),
            ("Copy", qtawesome.icon("mdi.content-copy")),
        ]
        super()._addActionButtons(
            layoutButtons, 
            NavActions=custom_nav, 
            CRUDActions=custom_crud
        )
```

#### `_handleActionButton(action)`

Dispatch button clicks to appropriate handler methods.

**Parameters:**
- `action` (str): Action name (case-insensitive)

**Standard Action Mappings:**
- "first" → `on_loadfirst_clicked()`
- "previous" → `on_loadprev_clicked()`
- "next" → `on_loadnext_clicked()`
- "last" → `on_loadlast_clicked()`
- "add" → `on_add_clicked()`
- "save" → `on_save_clicked()`
- "delete" → `on_delete_clicked()`
- "cancel" → `on_cancel_clicked()`

**Extending with Custom Actions:**
```python
class CustomForm(cSimpleRecordForm):
    def _handleActionButton(self, action):
        action = action.lower()
        if action == "copy":
            self.on_copy_clicked()
        elif action == "export":
            self.on_export_clicked()
        else:
            # Fall back to standard handlers
            super()._handleActionButton(action)
    
    def on_copy_clicked(self):
        """Create a duplicate of the current record."""
        # Implementation here
        pass
```

#### `on_cancel_clicked()`

Handle Cancel button click by closing the form.

**Note:** Currently just closes the form without confirmation. Override to add confirmation prompt if needed.

**Example Override:**
```python
def on_cancel_clicked(self):
    """Close form with unsaved changes confirmation."""
    if self.isDirty():
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, 'Confirm Close',
            'Close without saving changes?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.No:
            return
    self.close()
```

### Lookup Methods

#### `repopLookups()`

Refresh all lookup widgets with current database values.

Called automatically after save operations to ensure lookup lists are up-to-date.

**Note:** This overrides the base class stub implementation with functional behavior.

## Complete Usage Examples

### Example 1: Basic Form

```python
from PySide6.QtWidgets import QApplication, QLineEdit, QComboBox
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from calvincTools.utils.cQdbFormWidgets import cSimpleRecordForm

# Define ORM model
Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    department = Column(String(50))
    status = Column(String(20))

# Setup database
engine = create_engine('sqlite:///company.db')
Base.metadata.create_all(engine)
SessionMaker = sessionmaker(bind=engine)

# Create form class
class EmployeeForm(cSimpleRecordForm):
    _ORMmodel = Employee
    _ssnmaker = SessionMaker
    _formname = "Employee Editor"
    
    fieldDefs = {
        'name': {
            'label': 'Full Name',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (0, 0, 1, 2)
        },
        'department': {
            'label': 'Department',
            'widgetType': QComboBox,
            'page': 0,
            'position': (1, 0, 1, 1),
            'choices': ['Sales', 'Engineering', 'HR', 'Finance']
        },
        'status': {
            'label': 'Status',
            'widgetType': QComboBox,
            'page': 0,
            'position': (2, 0, 1, 1),
            'choices': ['Active', 'Inactive', 'On Leave']
        }
    }

# Run application
app = QApplication([])
form = EmployeeForm()
form.show()
app.exec()
```

### Example 2: Multi-Page Form

```python
class ProjectForm(cSimpleRecordForm):
    _ORMmodel = Project
    _ssnmaker = SessionMaker
    _formname = "Project Management"
    
    pages = ['General', 'Details', 'Team', 'Budget']
    
    fieldDefs = {
        # General page
        'project_name': {
            'label': 'Project Name',
            'widgetType': QLineEdit,
            'page': 'General',
            'position': (0, 0, 1, 2)
        },
        'project_code': {
            'label': 'Code',
            'widgetType': QLineEdit,
            'page': 'General',
            'position': (1, 0, 1, 1),
            'maximumWidth': 150
        },
        
        # Details page
        'description': {
            'label': 'Description',
            'widgetType': QTextEdit,
            'page': 'Details',
            'position': (0, 0, 3, 2)
        },
        
        # Team page
        '@manager_id': {
            'label': 'Project Manager',
            'widgetType': cDataList,
            'page': 'Team',
            'position': (0, 0, 1, 2)
        },
        
        # Budget page
        'budget': {
            'label': 'Budget',
            'widgetType': QLineEdit,
            'page': 'Budget',
            'position': (0, 0, 1, 1)
        }
    }
```

### Example 3: Form with Transformation Hooks

```python
class ContactForm(cSimpleRecordForm):
    _ORMmodel = Contact
    _ssnmaker = SessionMaker
    _formname = "Contact Manager"
    
    fieldDefs = {
        'name': {
            'label': 'Name',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (0, 0, 1, 2)
        },
        'email': {
            'label': 'Email',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (1, 0, 1, 2)
        },
        'phone': {
            'label': 'Phone',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (2, 0, 1, 1)
        }
    }
    
    def _transform_email(self, value):
        """Normalize email to lowercase."""
        return value.lower().strip() if value else value
    
    def _transform_phone(self, value):
        """Format phone number to (XXX) XXX-XXXX."""
        if not value:
            return value
        # Remove non-numeric
        digits = ''.join(c for c in value if c.isdigit())
        if len(digits) == 10:
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        return value
```

### Example 4: Custom Button Actions

```python
class InvoiceForm(cSimpleRecordForm):
    _ORMmodel = Invoice
    _ssnmaker = SessionMaker
    _formname = "Invoice Editor"
    
    fieldDefs = {
        # Field definitions...
    }
    
    def _addActionButtons(self, layoutButtons=None, **kwargs):
        """Add standard buttons plus Print and Email."""
        import qtawesome
        
        # Standard CRUD actions plus custom ones
        custom_crud = [
            ("Add", qtawesome.icon("mdi.plus")),
            ("Save", qtawesome.icon("mdi.content-save")),
            ("Delete", qtawesome.icon("mdi.delete")),
            ("Print", qtawesome.icon("mdi.printer")),
            ("Email", qtawesome.icon("mdi.email")),
        ]
        
        super()._addActionButtons(
            layoutButtons,
            CRUDActions=custom_crud
        )
    
    def _handleActionButton(self, action):
        """Handle standard and custom actions."""
        action = action.lower()
        if action == "print":
            self.on_print_clicked()
        elif action == "email":
            self.on_email_clicked()
        else:
            super()._handleActionButton(action)
    
    def on_print_clicked(self):
        """Print the current invoice."""
        if not self.currRec():
            self.showError("No invoice to print")
            return
        # Printing implementation...
        print(f"Printing invoice {self.currRec().id}")
    
    def on_email_clicked(self):
        """Email the current invoice."""
        if not self.currRec():
            self.showError("No invoice to email")
            return
        # Email implementation...
        print(f"Emailing invoice {self.currRec().id}")
```

### Example 5: Override Save Behavior

```python
class OrderForm(cSimpleRecordForm):
    _ORMmodel = Order
    _ssnmaker = SessionMaker
    _formname = "Order Entry"
    
    fieldDefs = {
        # Field definitions...
        'order_total': {
            'label': 'Total',
            'widgetType': QLineEdit,
            'page': 0,
            'position': (5, 0, 1, 1),
            'readonly': True
        }
    }
    
    def on_save_clicked(self, *_):
        """Save with validation and audit trail."""
        currRec = self.currRec()
        if not currRec:
            return
        
        # Validation
        if not currRec.customer_id:
            self.showError("Customer is required")
            return
        
        if not currRec.order_items:
            self.showError("Order must have at least one item")
            return
        
        # Calculate total before saving
        currRec.order_total = sum(item.amount for item in currRec.order_items)
        
        # Add audit trail
        from datetime import datetime
        currRec.last_modified = datetime.now()
        currRec.modified_by = self.current_user_id()
        
        # Call parent save
        super().on_save_clicked()
        
        # Additional post-save actions
        self.log_order_change(currRec.id)
    
    def current_user_id(self):
        """Get current user ID from application context."""
        # Implementation depends on your app structure
        return 1
    
    def log_order_change(self, order_id):
        """Log order changes to audit table."""
        # Audit logging implementation...
        pass
```

## Advanced Customization

### Custom Layout Arrangement

Override `_buildFormLayout()` to change the structure while keeping button functionality:

```python
class CustomLayoutForm(cSimpleRecordForm):
    def _buildFormLayout(self):
        """Custom layout with side panel."""
        from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel
        
        rtnDict = {}
        
        # Main horizontal layout
        layoutMain = QHBoxLayout(self)
        
        # Left side: standard form
        layoutLeft = QVBoxLayout()
        layoutFormHdr = QHBoxLayout()
        layoutFormPages = cstdTabWidget()
        layoutButtons = QHBoxLayout()
        
        lblFormName = cQFmNameLabel(self._formname, self)
        layoutFormHdr.addWidget(lblFormName)
        
        layoutLeft.addLayout(layoutFormHdr)
        layoutLeft.addWidget(layoutFormPages)
        layoutLeft.addLayout(layoutButtons)
        
        # Right side: info panel
        layoutRight = QVBoxLayout()
        infoLabel = QLabel("Additional Info", self)
        layoutRight.addWidget(infoLabel)
        # Add more widgets to right panel...
        
        # Combine
        layoutMain.addLayout(layoutLeft, stretch=3)
        layoutMain.addLayout(layoutRight, stretch=1)
        
        # Build return dictionary
        rtnDict['layoutMain'] = layoutMain
        rtnDict['layoutFormHdr'] = layoutFormHdr
        rtnDict['layoutForm'] = layoutFormPages
        rtnDict['layoutFormPages'] = layoutFormPages
        rtnDict['layoutButtons'] = layoutButtons
        
        self.setWindowTitle(self._formname)
        
        return rtnDict
```

### Vertical Button Layout

```python
class VerticalButtonForm(cSimpleRecordForm):
    def _addActionButtons(self, layoutButtons=None, **kwargs):
        """Stack buttons vertically on the right side."""
        super()._addActionButtons(
            layoutButtons,
            layoutHorizontal=False  # Stack vertically
        )
```

### Dialog-Style Form

Make the form work as a modal dialog:

```python
from PySide6.QtWidgets import QDialog

class PersonDialog(cSimpleRecordForm):
    _ORMmodel = Person
    _ssnmaker = SessionMaker
    _formname = "Edit Person"
    
    fieldDefs = {
        # Field definitions...
    }
    
    def __init__(self, person_id=None, parent=None):
        super().__init__(parent=parent)
        
        # Make it a dialog
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        
        # Load specific record if provided
        if person_id:
            self._load_record_by_id(person_id)
    
    def on_save_clicked(self, *_):
        """Save and close dialog."""
        super().on_save_clicked()
        if not self.isDirty():  # Save succeeded
            self.accept()
    
    def on_cancel_clicked(self):
        """Close dialog without saving."""
        self.reject()

# Usage
dialog = PersonDialog(person_id=123, parent=main_window)
if dialog.exec() == QDialog.DialogCode.Accepted:
    print("Person saved")
else:
    print("Cancelled")
```

## Tips and Best Practices

### 1. Form Naming
```python
# Good: Descriptive names
_formname = "Customer Contact Editor"
_formname = "Product Inventory Management"

# Avoid: Generic names
_formname = "Form"
_formname = "Edit"
```

### 2. Button Customization
```python
# Reuse standard icons from qtawesome
import qtawesome as qta

# Material Design Icons (mdi)
qta.icon("mdi.account")
qta.icon("mdi.content-save")
qta.icon("mdi.delete")

# Font Awesome
qta.icon("fa5s.user")
qta.icon("fa5s.save")

# With colors
qta.icon("mdi.delete", color='red')
qta.icon("mdi.content-save", color='green')
```

### 3. Status Bar Usage
```python
class MyForm(cSimpleRecordForm):
    def on_save_clicked(self, *_):
        """Save with status feedback."""
        super().on_save_clicked()
        
        sb = self.statusBar()
        if sb:
            sb.showMessage("Record saved successfully", 3000)  # 3 seconds
```

### 4. Form Validation
```python
def on_save_clicked(self, *_):
    """Validate before saving."""
    currRec = self.currRec()
    
    # Validate required fields
    if not currRec.name or not currRec.name.strip():
        self.showError("Name is required")
        return
    
    # Validate format
    if currRec.email and '@' not in currRec.email:
        self.showError("Invalid email format")
        return
    
    # Validate business rules
    if currRec.end_date < currRec.start_date:
        self.showError("End date cannot be before start date")
        return
    
    super().on_save_clicked()
```

### 5. Keyboard Shortcuts
```python
from PySide6.QtGui import QKeySequence, QShortcut

class MyForm(cSimpleRecordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self, self.on_save_clicked)
        QShortcut(QKeySequence("Ctrl+N"), self, self.on_add_clicked)
        QShortcut(QKeySequence("Ctrl+D"), self, self.on_delete_clicked)
        QShortcut(QKeySequence("Escape"), self, self.on_cancel_clicked)
```

## Common Patterns

### Pattern 1: Read-Only Form (Viewer)
```python
class RecordViewer(cSimpleRecordForm):
    def _addActionButtons(self, layoutButtons=None, **kwargs):
        """Only navigation buttons, no editing."""
        import qtawesome
        
        nav_only = [
            ("First", qtawesome.icon("mdi.page-first")),
            ("Previous", qtawesome.icon("mdi.arrow-left-bold")),
            ("Next", qtawesome.icon("mdi.arrow-right-bold")),
            ("Last", qtawesome.icon("mdi.page-last")),
            ("Close", qtawesome.icon("mdi.close")),
        ]
        
        super()._addActionButtons(
            layoutButtons,
            NavActions=nav_only,
            CRUDActions=[]
        )
    
    # Make all fields readonly
    def _placeFields(self, *args, **kwargs):
        super()._placeFields(*args, **kwargs)
        for widget in self._formWidgets.values():
            if hasattr(widget, 'setReadOnly'):
                widget.setReadOnly(True)
```

### Pattern 2: Wizard-Style Navigation
```python
class WizardForm(cSimpleRecordForm):
    def _addActionButtons(self, layoutButtons=None, **kwargs):
        """Back/Next instead of record navigation."""
        import qtawesome
        
        wizard_nav = [
            ("Back", qtawesome.icon("mdi.arrow-left")),
            ("Next", qtawesome.icon("mdi.arrow-right")),
        ]
        
        super()._addActionButtons(
            layoutButtons,
            NavActions=wizard_nav,
            CRUDActions=[("Save", qtawesome.icon("mdi.check"))]
        )
    
    def _handleActionButton(self, action):
        action = action.lower()
        if action == "back":
            self.go_to_previous_page()
        elif action == "next":
            self.go_to_next_page()
        else:
            super()._handleActionButton(action)
    
    def go_to_previous_page(self):
        """Navigate to previous tab."""
        current = self.layoutFormPages.currentIndex()
        if current > 0:
            self.layoutFormPages.setCurrentIndex(current - 1)
    
    def go_to_next_page(self):
        """Navigate to next tab."""
        current = self.layoutFormPages.currentIndex()
        if current < self.layoutFormPages.count() - 1:
            self.layoutFormPages.setCurrentIndex(current + 1)
```

### Pattern 3: Embedded Form (No Navigation)
```python
class EmbeddedDetailForm(cSimpleRecordForm):
    """Form for editing a single specific record (no navigation)."""
    
    def __init__(self, record_id, *args, **kwargs):
        self._fixed_record_id = record_id
        super().__init__(*args, **kwargs)
    
    def initialdisplay(self):
        """Load the specific record instead of first."""
        self._load_record_by_id(self._fixed_record_id)
    
    def _addActionButtons(self, layoutButtons=None, **kwargs):
        """Only Save and Cancel."""
        import qtawesome
        
        super()._addActionButtons(
            layoutButtons,
            NavActions=[],
            CRUDActions=[
                ("Save", qtawesome.icon("mdi.content-save")),
                ("Cancel", qtawesome.icon("mdi.cancel")),
            ]
        )
```

## Troubleshooting

### Issue: Buttons Not Appearing
**Cause:** `_addActionButtons()` not creating `self.btnCommit`  
**Solution:** Ensure at least one button is named "Save" to create the commit button reference

```python
def _addActionButtons(self, layoutButtons=None, **kwargs):
    # Must have a "Save" button for btnCommit reference
    actions = [
        ("Save", icon),  # This creates self.btnCommit
        # ... other buttons
    ]
```

### Issue: Form Title Not Showing
**Cause:** `_formname` not set before layout creation  
**Solution:** Set `_formname` as class attribute or in constructor before super().__init__()

```python
class MyForm(cSimpleRecordForm):
    _formname = "My Form Title"  # Set as class attribute
    
# OR

def __init__(self, *args, **kwargs):
    self._formname = "My Form Title"  # Set before super()
    super().__init__(*args, **kwargs)
```

### Issue: Lookup Widgets Not Refreshing
**Cause:** `repopLookups()` not being called or not implemented  
**Solution:** Ensure you're using `cSimpleRecordForm` (not base class) which implements this

### Issue: Custom Buttons Not Working
**Cause:** Action name not handled in `_handleActionButton()`  
**Solution:** Override and handle custom action names

```python
def _handleActionButton(self, action):
    if action.lower() == "myaction":
        self.on_my_action()
    else:
        super()._handleActionButton(action)
```

## Related Classes

- **cSimpleRecordForm_Base**: Abstract base class (see [cSimpleRecordForm_Base.md](./cSimpleRecordForm_Base.md))
- **cSimpRecFmElement_Base**: Base class for form field adapters
- **cQFmFldWidg**: Standard form field widget wrapper
- **cQFmLookupWidg**: Lookup field widget wrapper
- **cSimpleRecordSubForm1**: Subform for one-to-many relationships
- **cSimpRecSbFmRecord**: Subform with full record editing

## See Also

- [Form classes.md](./Form%20classes.md): Overview of form class hierarchy
- [cSimpleRecordForm_Base.md](./cSimpleRecordForm_Base.md): Base class documentation
- [database.md](./database.md): Database integration details
- [QtAwesome Documentation](https://qtawesome.readthedocs.io/): Icon reference
