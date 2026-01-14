from typing import (Dict, List, Mapping, Tuple, Any, )
import copy

import webbrowser

from PySide6.QtCore import (Qt, QObject,
    Signal, Slot, 
    QAbstractTableModel, QModelIndex, )
from PySide6.QtGui import (QFont, QIcon, )
from PySide6.QtWidgets import ( QBoxLayout, QLayout, QStyle, QTabWidget, 
    QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QFrame, 
    QTableView, QHeaderView, QScrollArea,
    QDialog, QMessageBox, QFileDialog, QDialogButtonBox,
    QLabel, QLCDNumber, QLineEdit, QTextEdit, QPlainTextEdit, QPushButton, QCheckBox, QComboBox, QDateEdit,
    QRadioButton, QGroupBox, QButtonGroup, 
    QSizePolicy, 
    )

from openpyxl import Workbook
from sqlalchemy import (inspect, select, Engine, ) 
from sqlalchemy.orm.session import make_transient


# there's no need to import cMenu, plus it's a circular ref - cMenu depends heavily on this module
# from .kls_cMenu import cMenu 

from .apphooks import cTools_apphooks
from .database import (
    get_cMenu_sessionmaker, get_cMenu_session, 
    Repository,
    )
from .dbmenulist import (MenuRecords, newgroupnewmenu_menulist, newmenu_menulist, )
# from sysver import sysver
from .menucommand_constants import MENUCOMMANDS, COMMANDNUMBER
from .models import (menuItems, menuGroups, )
from .utils import (
    recordsetList,
    cSimpleRecordForm_Base, cSimpleRecordForm, cQFmConstants,
    cComboBoxFromDict, 
    cstdTabWidget, cGridWidget,
    areYouSure, 
    cQFmNameLabel, 
    SQLAlchemySQLQueryModel,
    UnderConstruction_Dialog,
    Excelfile_fromqs, ExcelWorkbook_fileext,
    pleaseWriteMe,  
    )

# copied from cMenu - if you change it here, change it there
_NUM_menuBUTTONS:int = 20
_NUM_menuBUTNCOLS:int = 2
_NUM_menuBTNperCOL: int = int(_NUM_menuBUTTONS/_NUM_menuBUTNCOLS)

Nochoice = {'---': None}    # only needed for combo boxes, not datalists

# fontFormTitle = QFont()
# fontFormTitle.setFamilies([u"Copperplate Gothic"])
# fontFormTitle.setPointSize(24)


def FormBrowse(parntWind, 
    formname, 
    *args, **kwargs
    ) -> Any|None:
    urlIndex = 0
    viewIndex = 1

    FormNameToURL_Map:Dict[str,Tuple[str,Any]] = cTools_apphooks().get_FormNameToURL_Map()
    
    # theForm = 'Form ' + formname + ' is not built yet.  Calvin needs more coffee.'
    theForm = None
    # formname = formname.lower()
    if formname in FormNameToURL_Map:
        if FormNameToURL_Map[formname][urlIndex]:
            # figure out how to repurpose this later
            # url = FormNameToURL_Map[formname][urlIndex]
            # try:
            #     theView = resolve(reverse(url)).func
            #     urlExists = True
            # except (Resolver404, NoReverseMatch):
            #     urlExists = False
            # # end try
            # if urlExists:
            #     theForm = theView(req)
            # else:
            #     formname = f'{formname} exists but url {url} '
            # #endif
            pass
        # endif FormNameToURL_Map[formname][urlIndex]:
        # elif FormNameToURL_Map[formname][viewIndex]:
        if FormNameToURL_Map[formname][viewIndex]:
            fn = None
            try:
                fn = FormNameToURL_Map[formname][viewIndex]
                theForm = fn(*args, **kwargs)
            except NameError:
                # fn = None
                formname = f'{formname} exists but view {FormNameToURL_Map[formname][viewIndex]}'
            #end try
        # endif FormNameToURL_Map[formname][viewIndex]:
    # endif formname in FormNameToURL_Map:
    if not theForm:
        formname = f'Form {formname} is not built yet.  Calvin needs more coffee.'
        # print(formname)
        UnderConstruction_Dialog(parntWind, formname).show()
    else:
        # print(f'about to show {theForm}')
        # theForm.show()
        # print(f'done showing')
        return theForm
    # endif

    # must be rendered if theForm came from a class-based-view
    # if hasattr(theForm,'render'): theForm = theForm.render()
    # return theForm

def ShowTable(parntWind, tblname, FormNameToURL_Map):
    # showing a table is nothing more than another form
    return FormBrowse(parntWind,tblname, FormNameToURL_Map)

#####################################################
#####################################################

class QWGetSQL(QWidget):
    runSQL = Signal(str)    # Emitted with the SQL string when run is clicked
    cancel = Signal()       # Emitted when cancel is clicked    
    
    def __init__(self, parent = None):
        super().__init__(parent)

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('Enter SQL'))
        self.setWindowTitle(self.tr('Enter SQL'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        self.layoutFormHdr.addSpacing(20)
        
        # main area for entering SQL
        self.layoutFormMain = QFormLayout()
        self.txtedSQL = QTextEdit()
        self.layoutFormMain.addRow(self.tr('SQL statement'), self.txtedSQL)
        
        # run/Cancel buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonRunSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.Computer), self.tr('Run SQL') ) 
        self.buttonRunSQL.clicked.connect(self._on_run_sql_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonRunSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Cancel') ) 
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)
        
        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)
        horzline2 = QFrame()
        horzline2.setFrameShape(QFrame.Shape.HLine)
        horzline2.setFrameShadow(QFrame.Shadow.Sunken)
        
        # status message
        self.lblStatusMsg = QLabel()
        self.lblStatusMsg.setText('\n\n')
        
        # Hints
        self.lblHints = QPlainTextEdit()
        self.lblHints.setReadOnly(True)

        # read txtHints from file
        hintFile = 'assets/SQLHints.txt'
        try:
            with open(hintFile, 'r', encoding='utf-8') as f:
                txtHints = f.read()
        except Exception:
            txtHints = 'PRAGMA table_list;\nPRAGMA table_xinfo(tablname);'
        self.lblHints.setPlainText(txtHints)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addLayout(self.layoutFormActionButtons)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addWidget(self.lblStatusMsg)
        self.layoutForm.addWidget(horzline2)
        self.layoutForm.addWidget(self.lblHints)
        
    def _on_run_sql_clicked(self):
        # Emit the runSQL signal with the text from the editor.
        sql_text = self.txtedSQL.toPlainText()
        self.runSQL.emit(sql_text)

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.cancel.emit()        

    def closeEvent(self, event):
        self.cancel.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)

class QWShowSQL(QWidget):
    ReturnToSQL = Signal()
    closeMe = Signal()
    closeBoth = Signal()
    
    def __init__(self, qmodel:SQLAlchemySQLQueryModel, parent:QWidget|QObject|None = None):
        if isinstance(parent, QWidget) or parent is None:
            super().__init__(parent)

        # save incoming for future use if needed
        self._qmodel = qmodel
        origSQL = qmodel.query()
        # # rowCount will not return true count if not all rows fetched
        # # no longer true?
        # while qmodel.canFetchMore():
        #     qmodel.fetchMore()
        numrows = qmodel.rowCount()
        colNames = [qmodel.headerData(x,Qt.Orientation.Horizontal) for x in range(qmodel.columnCount())]

        font = QFont()
        font.setPointSize(12)
        self.setFont(font)
        
        self.layoutForm = QVBoxLayout(self)
        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('SQL Results'))
        self.setWindowTitle(self.tr('SQL Results'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        
        self.layoutFormSQLDescription = QFormLayout()
        lblOrigSQL = QLabel()
        lblOrigSQL.setText(origSQL)
        lblnRecs = QLabel()
        lblnRecs.setText(f'{numrows}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormSQLDescription.addRow('SQL Entered:', lblOrigSQL)
        self.layoutFormSQLDescription.addRow('rows affctd:', lblnRecs)
        self.layoutFormSQLDescription.addRow('cols:', lblcolNames)
        

        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()
        
        resultTable = QTableView()
        # resultTable.verticalHeader().setHidden(True)
        header = resultTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        resultTable.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        resultTable.setModel(qmodel)
        self.layoutFormMain.addWidget(resultTable)
        
        #  buttons
        self.layoutFormActionButtons = QHBoxLayout()
        self.buttonGetSQL = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.GoPrevious), self.tr('Back to SQL') ) 
        self.buttonGetSQL.clicked.connect(self._return_to_sql)
        self.layoutFormActionButtons.addWidget(self.buttonGetSQL, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonDLResults = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave), self.tr('D/L Results') ) 
        self.buttonDLResults.clicked.connect(self.DLResults)
        self.layoutFormActionButtons.addWidget(self.buttonDLResults, alignment=Qt.AlignmentFlag.AlignRight)
        self.buttonCancel = QPushButton( QIcon.fromTheme(QIcon.ThemeIcon.WindowClose), self.tr('Close') ) 
        self.buttonCancel.clicked.connect(self._on_cancel_clicked)
        self.layoutFormActionButtons.addWidget(self.buttonCancel, alignment=Qt.AlignmentFlag.AlignRight)
        
        # generic horizontal lines
        horzline = QFrame()
        horzline.setFrameShape(QFrame.Shape.HLine)
        horzline.setFrameShadow(QFrame.Shadow.Sunken)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormSQLDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        self.layoutForm.addWidget(horzline)
        self.layoutForm.addLayout(self.layoutFormActionButtons)
        
        colfctr = 90
        self.setMinimumWidth(colfctr*len(colNames))
        
    @Slot()
    def DLResults(self):
        ExcelFileNamePrefix = "SQLresults"
        # Create a dictionary of records from the model
        row_count = self._qmodel.rowCount()
        col_count = self._qmodel.columnCount()
        column_names = [self._qmodel.headerData(i, Qt.Orientation.Horizontal) for i in range(col_count)]

        Excel_qdict = []
        for row in range(row_count):
            record = {}
            for col in range(col_count):
                value = self._qmodel.data(self._qmodel.index(row, col))
                record[column_names[col]] = value
            Excel_qdict.append(record)

        # Create an Excel workbook and save it
        xlws = Excelfile_fromqs(Excel_qdict)
        filName, _ = QFileDialog.getSaveFileName(self, 
            caption="Enter Spreadsheet File Name",
            filter=f'{ExcelFileNamePrefix}*{ExcelWorkbook_fileext}',
            selectedFilter=f'*{ExcelWorkbook_fileext}'
        )
        if filName and isinstance(xlws, Workbook):
            xlws.save(filName)     
        
    def _return_to_sql(self):
        self.ReturnToSQL.emit()

    def _on_cancel_clicked(self):
        # Emit the cancel signal.
        self.closeBoth.emit()        

    def closeEvent(self, event):
        self.closeMe.emit()  # Emit the signal
        event.accept()  # Accept the close event (allows the window to close)
# QWShowSQL

class cMRunSQL(QWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        app_sessionmaker = cTools_apphooks().get_app_sessionmaker()
        assert app_sessionmaker is not None, "app_sessionmaker must be provided"
        self.app_sessionmaker = app_sessionmaker
        
        self.inputSQL:str|None = None
        self.qmodel:SQLAlchemySQLQueryModel
        self.colNames:str|List[str]|None = None
        self.wndwAlive:Dict[str,bool] = {}
        
        self.wndwGetSQL = QWGetSQL(parent)
        self.wndwGetSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwGetSQL.runSQL.connect(self.rawSQLexec)
        self.wndwGetSQL.cancel.connect(self._on_cancel)
        self.wndwAlive['Get'] = True
        self.wndwGetSQL.destroyed.connect(lambda: self.wndwDest('Get'))
        
        self.wndwShowSQL: QWShowSQL     # will be redefined later

    def wndwDest(self, whichone:str):
        self.wndwAlive[whichone] = False
        
    def show(self):
        self.wndwGetSQL.show()

    @Slot(str)  #type: ignore
    def rawSQLexec(self, inputSQL:str):
        #TODO: choose session - put in user control
        engine = self.app_sessionmaker().get_bind()

        self.qmodel = SQLAlchemySQLQueryModel(inputSQL, engine)

        self.rawSQLshow()
            
    def rawSQLshow(self):
        self.wndwShowSQL = QWShowSQL(self.qmodel, self.parent())
        self.wndwShowSQL.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.wndwShowSQL.ReturnToSQL.connect(self._ShowToGetSQL)
        self.wndwShowSQL.closeBoth.connect(self._on_cancel)

        self.wndwAlive['Show'] = True
        self.wndwShowSQL.destroyed.connect(lambda: self.wndwDest('Show'))


        self.wndwGetSQL.hide()
        self.wndwShowSQL.show()

    @Slot()
    def _ShowToGetSQL(self):
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        self.wndwGetSQL.show()
        
    @Slot()
    def _on_cancel(self):
        # Handle the cancellation by closing both windows.
        self._close_all()

    def _close_all(self):
        # Close the child widget if it exists.
        if self.wndwAlive.get('Get'):
            self.wndwGetSQL.close()
        if self.wndwAlive.get('Show'):
            self.wndwShowSQL.close()
        # Close this widget (cMRunSQL) as well.
        self.close()
# cMRunSQL

#############################################
#############################################
#############################################

class cWidgetMenuItem(cSimpleRecordForm_Base):
    """
    cWidgetMenuItem_tst
    -------------------
    A specialized form widget for viewing and editing a single menu item record (menuItems).
    This widget is intended to be used inside a QWidget-based application using PyQt/PySide
    and SQLAlchemy for persistence. It builds a compact edit form from the `fieldDefs`
    mapping and provides common CRUD-related actions appropriate for a menu item:
    - Save changes (commit)
    - Remove the current option
    - Copy or Move the current option to another menu/position
    Notes
    -----
    - This widget expects an SQLAlchemy mapped ORM model `menuItems` and a sessionmaker
        callable `cMenu_Session` to be available and assigned to the class attributes
        `_ORMmodel` and `_ssnmaker` respectively.
    - The widget does not create brand-new menu items in the sense of offering a primary
        "new" flow; it operates on an existing `menuItems` instance supplied at construction.
    - Copy semantics use `copy.deepcopy` followed by `sqlalchemy.orm.session.make_transient`
        to detach the copy before inserting it as a new row. Move semantics create a copy
        and then remove the original row from the database.
    - The widget emits the `requestMenuReload` Signal() whenever a change is made that
        requires other components to refresh their cached menu structures.
    Public attributes (class-level)
    -------------------------------
    - _ORMmodel: ORM model class for menu items (expected: menuItems)
    - _ssnmaker: sessionmaker factory for database transactions (expected: cMenu_Session)
    - fieldDefs: dict mapping field names to widget configuration for form construction
    - requestMenuReload: Qt Signal emitted when a menu reload is required by listeners
    Inner class: cEdtMnuItmDlg_CopyMove_MenuItm
    ------------------------------------------
    A modal QDialog used to prompt the user for a destination Menu Group, Menu ID,
    and Option Number when copying or moving a menu option. It encapsulates all UI and
    validation required to choose a valid destination (e.g., preventing collisions with
    already-defined option numbers):
    Key behaviors / API:
    - __init__(menuGrp:int, menuID:int, optionNumber:int, parent:QWidget|None)
        Constructs the dialog initializing comboboxes for menu groups, menus, and options.
    - dictmenuGroup() -> Dict[str,int]
        Returns mapping of menu group names to ids using the cMenu_Session.
    - dictmenus(mnuGrp:int) -> Mapping[str, int|None]
        Returns mapping of main-menu OptionText -> MenuID for menus in the supplied group.
    - dictmenuOptions(mnuID:int) -> Mapping[str, int|None]
        Returns the set of available option numbers (as strings) for a target menu id,
        excluding option numbers already defined in that menu.
    - loadMenuIDs(idx:int), loadMenuOptions(idx:int), menuOptionChosen(idx:int)
        Slots used to cascade the combobox population and enable/disable the Ok button.
    - enableOKButton()
        Enables the Ok button only when a Group, Menu and Option are all selected.
    - exec_CM_MItm() -> Tuple[int|bool, bool, Tuple[int,int,int]]
        Executes the dialog (modal) and returns a tuple:
            (exec_result, is_copy_bool, (chosenGroup, chosenMenu, chosenOption))
        where exec_result is the QDialog exec() return, and is_copy_bool is True for Copy,
        False for Move.
    Public instance methods (high-level)
    ------------------------------------
    - __init__(menuitmRec: menuItems, parent: QWidget|None = None)
        Initialize the widget to operate on the provided menu item ORM instance. The
        supplied record is considered the "current record" for subsequent operations.
    - _buildFormLayout() -> tuple[QBoxLayout, QTabWidget, QBoxLayout|None]
        Internal layout builder that returns tuple of left tab widget and right layout
        containers used by the base form assembly.
    - _addActionButtons()
        Constructs and wires action buttons (Save Changes, Copy / Move, Remove) and places
        them into the widget's button layout. Buttons are connected to on_save_clicked,
        copyMenuOption, and on_delete_clicked respectively.
    - _handleActionButton(action: str) -> None
        Overridden no-op; action routing is handled locally.
    - _finalizeMainLayout()
        Assembles form, action buttons, and other parts into the main layout.
    - fillFormFromcurrRec()
        Populate the form widgets from the currently-bound record. Also updates button
        enablement: Copy/Move and Remove are disabled for new (unsaved) records.
    - initialdisplay()
        Convenience method that calls fillFormFromcurrRec() to prime the UI.
    - on_delete_clicked() -> None
        Slot executed when the Remove button is clicked. Behavior:
            - Confirms deletion with the user (via areYouSure).
            - Loads the persistent record by primary key and deletes it in a session, then commits.
            - Reinitializes the current record object kept by the widget and restores the
                MenuGroup/MenuID/OptionNumber values so the user can create or reassign a new
                option in the same slot if desired.
            - Emits requestMenuReload to inform listeners that menu data changed.
        Preconditions:
            - self._ssnmaker (class attribute) must be available.
            - self._ORMmodel must refer to the mapped ORM model.
    - copyMenuOption() -> None
        Slot launched by the Copy / Move button. Behavior:
            - Opens the inner cEdtMnuItmDlg_CopyMove_MenuItm dialog to request a destination.
            - If the user accepts:
                    * Creates a deep-copy of the in-memory record, detaches it (make_transient),
                        resets primary keys and target MenuGroup/MenuID/OptionNumber, and inserts it
                        into the database (session.add + commit).
                    * If the Move option was selected, deletes the original persistent record and
                        refreshes the widget's current record to a fresh, unpersisted instance bound
                        to the same original MenuGroup/MenuID/OptionNumber (so the UI remains stable).
            - Emits requestMenuReload when a move occurs (or when appropriate after copy).
        Implementation details:
            - The copy preserves relationships where deepcopy copies them; using make_transient
                is necessary to convert the copy into a state suitable for insertion.
            - The code ensures the sessionmaker and ORMmodel exist before performing DB actions.
    Signals
    -------
    - requestMenuReload: emitted after operations that require other UI components to
        reload/rebuild menus (e.g., delete, move).
    Error handling and assumptions
    ------------------------------
    - The widget assumes a working SQLAlchemy environment and valid ORM mappings for
        menuGroups and menuItems.
    - Database operations are transactional and use the provided cMenu_Session context.
    - UI routines assume typical Qt widget behavior and that combobox widgets expose
        .currentData(), .currentIndex(), .replaceDict(), .setCurrentIndex(), .clear() etc.
        (cComboBoxFromDict is expected to implement replaceDict and to use the data role
        for stored ids).
    - The widget will do nothing (no exception) if invoked when there is no current record,
        or if required class attributes (sessionmaker/ORM model) are not set; assertions are
        used in some code paths to surface incorrect configuration early.
    Example use
    -----------
    Create an instance of the widget bound to a loaded menuItems ORM instance and add it
    to a parent container. Wire to requestMenuReload to update surrounding UI:
            w = cWidgetMenuItem_tst(my_menuitem_record, parent=some_parent_widget)
            w.requestMenuReload.connect(on_reload_needed)
    This docstring documents the public behaviors and expectations of cWidgetMenuItem_tst.
    """
    _ORMmodel = menuItems
    _ssnmaker = get_cMenu_sessionmaker()
    fieldDefs = {
        'OptionNumber': {'label': 'Option Number', 'widgetType': QLineEdit, 'position': (0,0), 'noedit': True, 'readonly': True, 'frame': False, 'maximumWidth': 25, 'focusPolicy': Qt.FocusPolicy.NoFocus, 'focusable': Qt.FocusPolicy.NoFocus, },
        'OptionText': {'label': 'OptionText', 'widgetType': QLineEdit, 'position': (0,1,1,2)},
        'TopLine': {'label': 'Top Line', 'widgetType': QCheckBox, 'position': (0,3,1,2), 'lblChkBxYesNo': {True:'YES', False:'NO'}, },
        'BottomLine': {'label': 'Btm Line', 'widgetType': QCheckBox, 'position': (0,5), 'lblChkBxYesNo': {True:'YES', False:'NO'}, },
        'Command': {'label': 'Command', 'widgetType': cComboBoxFromDict, 'choices': vars(COMMANDNUMBER), 'position': (1,0,1,2)},
        'Argument': {'label': 'Argument', 'widgetType': QLineEdit, 'position': (1,2,1,2), },
        'PWord': {'label': 'Password', 'widgetType': QLineEdit, 'position': (1,4,1,2), },
    }

    # formFields:Dict[str, QWidget] = {}

    requestMenuReload:Signal = Signal()

    class cEdtMnuItmDlg_CopyMove_MenuItm(QDialog):

        intCMChoiceCopy:int = 10
        intCMChoiceMove:int = 20

        def __init__(self, menuGrp:int, menuID:int, optionNumber:int, parent = None):   # parent:QWidget = None
            super().__init__(parent)

            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu Item')

            self.dlgButtons = None # self.dlgButtons:QDialogButtonBoxto be defined later, but must exist now

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu Item {menuID}, {optionNumber}'))

            ##################################################
            # set up menuGroup, menuID, menuOption comboboxes
            layoutNewItemID = QGridLayout()

            lblMenuGroupID = QLabel(self.tr('Menu Group'))
            self.combobxMenuGroupID = cComboBoxFromDict(self.dictmenuGroup(), parent=self)
            self.combobxMenuGroupID.activated.connect(self.loadMenuIDs)

            lblMenuID = QLabel(self.tr('Menu'))
            self.combobxMenuID = cComboBoxFromDict(dict(self.dictmenus(menuGrp)), parent=self)
            # self.loadMenuIDs(menuGrp) - not necessary - done with initialization
            self.combobxMenuID.activated.connect(self.loadMenuOptions)

            lblMenuOption = QLabel(self.tr('Option'))
            self.combobxMenuOption = cComboBoxFromDict({}, parent=self)
            self.combobxMenuOption.activated.connect(self.menuOptionChosen)

            layoutNewItemID.addWidget(lblMenuGroupID,0,0)
            layoutNewItemID.addWidget(self.combobxMenuGroupID,1,0)
            layoutNewItemID.addWidget(lblMenuID,0,1)
            layoutNewItemID.addWidget(self.combobxMenuID,1,1)
            layoutNewItemID.addWidget(lblMenuOption,0,2)
            layoutNewItemID.addWidget(self.combobxMenuOption,1,2)

            self.combobxMenuGroupID.setCurrentIndex(self.combobxMenuGroupID.findData(menuGrp))
            self.loadMenuIDs(menuGrp)
            ##################################################            

            visualgrpboxCopyMove = QGroupBox(self.tr("Copy / Move"))
            layoutgrpCopyMove = QHBoxLayout()
            # Create radio buttons
            radioCopy = QRadioButton(self.tr("Copy"))
            radioMove = QRadioButton(self.tr("Move"))
            # Add radio buttons to the layout
            layoutgrpCopyMove.addWidget(radioCopy)
            layoutgrpCopyMove.addWidget(radioMove)
            visualgrpboxCopyMove.setLayout(layoutgrpCopyMove)
            # Create a QButtonGroup for logical grouping
            self.lgclbtngrpCopyMove = QButtonGroup()
            self.lgclbtngrpCopyMove.addButton(radioCopy, id=self.intCMChoiceCopy)
            self.lgclbtngrpCopyMove.addButton(radioMove, id=self.intCMChoiceMove)
            # Add the QGroupBox to the main layout

            self.dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            self.dlgButtons.accepted.connect(self.accept)
            self.dlgButtons.rejected.connect(self.reject)
            self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)

            layoutMine = QVBoxLayout()
            layoutMine.addWidget(lblDlgTitle)
            layoutMine.addWidget(visualgrpboxCopyMove)
            layoutMine.addLayout(layoutNewItemID)
            layoutMine.addWidget(self.dlgButtons)

            self.setLayout(layoutMine)
        # __init__
        
        ##########################################
        ########    execute this dialog

        def exec_CM_MItm(self) -> Tuple[int|bool, bool, Tuple[int, int, int]]:
            ret = super().exec()
            copymove = self.lgclbtngrpCopyMove.checkedId()
            chosenMenuGroup = self.combobxMenuGroupID.currentData()
            chosenMenuID = self.combobxMenuID.currentData()
            chosenMenuOption = self.combobxMenuOption.currentData()
            return (
                ret,
                copymove != self.intCMChoiceMove,   # True unless Move checked
                # return (Group, Menu, OptrNum) tuple
                (chosenMenuGroup, chosenMenuID, chosenMenuOption),
                )
        # exec_CM_MItm

        ##########################################
        ########    menu and Group dicts

        def dictmenuGroup(self) -> Dict[str, int]:
            return MenuRecords.menuGroupsDict()
        # dictmenuGroup
            
        def dictmenus(self, mnuGrp:int) -> Mapping[str, int|None]:
            retDict = Nochoice | MenuRecords.menuListDict(mnuGrp)
            return retDict
        # dictmenus
        
        def dictmenuOptions(self, mnuID:int) -> Mapping[str, int|None]:
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            listmenuItems = recordsetList(menuItems, retFlds=['OptionNumber'], where=f'MenuID={mnuID} AND MenuGroup_id={mnuGrp}', ssnmaker=get_cMenu_sessionmaker())
            definedOptions = {rec['OptionNumber'] for rec in listmenuItems}
            # Nochoice = {'---': None}  # only needed for combo boxes, not datalists
            return Nochoice | { str(n+1): n+1 for n in range(_NUM_menuBUTTONS) if n+1 not in definedOptions }
            # MenuRecords.menuDict(mnuGrp, mnuID)
        # dictmenuOptions

        ##########################################
        ########    getters/setters

        ##########################################
        ########    Create

        ##########################################
        ########    Read

        @Slot(int)  #type: ignore
        def loadMenuIDs(self, idx:int):
            mnuGrp:int = self.combobxMenuGroupID.currentData()
            # if self.combobxMenuGroupID.currentIndex() != -1:
            if mnuGrp is not None:
                self.combobxMenuID.replaceDict(dict(self.dictmenus(mnuGrp)))
            self.combobxMenuID.setCurrentIndex(-1)
            self.combobxMenuOption.clear()
            self.enableOKButton()
        # loadMenuIDs
        
        @Slot(int) #type: ignore
        def loadMenuOptions(self, idx:int):
            mnuID:int = self.combobxMenuID.currentData()
            #if self.combobxMenuID.currentIndex() != -1:
            if mnuID is not None:
                self.combobxMenuOption.replaceDict(dict(self.dictmenuOptions(mnuID)))
            self.combobxMenuOption.setCurrentIndex(-1)
            self.enableOKButton()
        # loadMenuOptions
        
        ##########################################
        ########    Update

        ##########################################
        ########    Delete

        ##########################################
        ########    object status

        ##########################################
        ########    widget-responding procs

        @Slot(int)  #type: ignore
        def menuOptionChosen(self, idx:int):
            self.enableOKButton()
        # menuOptionChosen
        def enableOKButton(self):
            if not self.dlgButtons:
                return
            all_GrpIdOption_chosen = all([
                self.combobxMenuGroupID.currentIndex() != -1,
                self.combobxMenuID.currentIndex() != -1,
                self.combobxMenuOption.currentIndex() != -1,
            ])
            self.dlgButtons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(all_GrpIdOption_chosen)
        # enableOKButton


    def __init__(self, menuitmRec:menuItems, parent:QWidget = None):   # type: ignore

        self.setcurrRec(menuitmRec)
        super().__init__(parent=parent)

        font = QFont()
        font.setPointSize(7)
        self.setFont(font)

        self.setObjectName('cWidgetMenuItem')

    # __init__

    ##########################################
    ########    Layout

    # def _buildFormLayout(self) -> tuple[QBoxLayout, QTabWidget, QBoxLayout | None]:
    def _buildFormLayout(self) -> Dict[str, QWidget|QLayout|None]:
        
        rtnDict: Dict[str, QWidget|QLayout|None] = {}

        layoutMain = QVBoxLayout(self)
        layoutMain.setContentsMargins(0,0,0,0)
        layoutMain.setSpacing(0)

        layoutFormMain = QHBoxLayout()
        layoutFormMain.setContentsMargins(0,0,0,0)
        layoutFormMain.setSpacing(0)

        layoutFormMainLeft = cstdTabWidget()
        layoutFormMainLeft.setContentsMargins(0,0,0,0)

        layoutFormMainRight = QVBoxLayout()
        layoutFormMainRight.setContentsMargins(0,0,0,0)
        layoutFormMainRight.setSpacing(0)

        layoutFormMain.addWidget(layoutFormMainLeft)
        layoutFormMain.addLayout(layoutFormMainRight)
        
        rtnDict['layoutMain'] = layoutMain
        rtnDict['layoutForm'] = layoutFormMain
        rtnDict['layoutFormPages'] = layoutFormMainLeft
        rtnDict['layoutButtons'] = layoutFormMainRight
        
        return rtnDict
    # _buildFormLayout
    def _finalizeMainLayout(self, layoutMain: QVBoxLayout, items: List | Tuple) -> None:
        items = [self.dictFormLayouts.get('layoutForm', None)]
        return super()._finalizeMainLayout(layoutMain, items)

    def _addActionButtons(self, 
            layoutButtons:QBoxLayout|None = None,
            layoutHorizontal: bool = True, 
            NavActions: list[tuple[str, QIcon]]|None = None,
            CRUDActions: list[tuple[str, QIcon]]|None = None,
            ) -> None:
        self.btnCommit = QPushButton(self.tr('Save\nChanges'), self)
        self.btnCommit.clicked.connect(self.on_save_clicked)
        # self.btnCommit.setFixedSize(60, 30)  # Adjust width and height
        self.btnCommit.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnMoveCopy = QPushButton(self.tr('Copy / Move'), self)
        self.btnMoveCopy.clicked.connect(self.copyMenuOption)
        # self.btnMoveCopy.setFixedSize(60, 30)  # Adjust width and height
        self.btnMoveCopy.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        self.btnRemove = QPushButton(self.tr('Remove'), self)
        self.btnRemove.clicked.connect(self.on_delete_clicked)
        # self.btnRemove.setFixedSize(60, 30)  # Adjust width and height
        self.btnRemove.setStyleSheet("padding: 2px; margin: 0;")  # Remove extra padding

        assert isinstance(layoutButtons, QBoxLayout), 'layoutButtons must be a Box Layout'
        layoutButtons.addWidget(self.btnMoveCopy)
        layoutButtons.addWidget(self.btnRemove)
        layoutButtons.addWidget(self.btnCommit)
    def _handleActionButton(self, action: str) -> None:
        # we have our own handlers, so no need to handle anything here
        return
    # _addActionButtons, _handleActionButton    


    ######################################################
    ########    Display 

    def fillFormFromcurrRec(self):
        super().fillFormFromcurrRec()

        self.btnMoveCopy.setEnabled(not self.isNewRecord())
        self.btnRemove.setEnabled(not self.isNewRecord())
    # fillFormFromRec

    def initialdisplay(self):
        self.fillFormFromcurrRec()
    # initialdisplay()

    ##########################################
    ########    Create

    # this widget doesn't create new records

    ##########################################
    ########    Read


    ##########################################
    ########    Update

    @Slot()     #type: ignore
    # def changeField(self):
    def changeField(self, wdgt, dbField, wdgt_value, force=False):
        super().changeField(wdgt, dbField, wdgt_value, force=False)
    # changeField

    @Slot()
    def on_save_clicked(self):
        super().on_save_clicked()
        self.requestMenuReload.emit()   # let listeners know we need a menu reload
    # on_save_clicked

    ##########################################
    ########    Delete

    @Slot()
    def on_delete_clicked(self):
        currRec = self.currRec()
        if not currRec:
            return

        mGrp, mnu, mOpt = (currRec.MenuGroup_id, currRec.MenuID, currRec.OptionNumber)

        pKey = self.primary_key()
        keyID = getattr(currRec, pKey.key)

        really = areYouSure(self,
            title="Remove Menu Option?",
            areYouSureQuestion=f'Really remove menu option {mGrp}, {mnu}, {mOpt} ({currRec.OptionText}) ?'
            )
        if really != QMessageBox.StandardButton.Yes:
            return

        # Actually delete
        ssnmkr = self.ssnmaker()
        assert ssnmkr is not None, "Sessionmaker must be set before touching the database"
        modl = self.ORMmodel()
        assert modl is not None, "ORMmodel must be set before deleting record"
        Repository(ssnmkr, modl).remove(currRec)

        self.initializeRec()
        # preserve MenuGroup, MenuID, OptionNumber
        currRec = self.currRec()
        currRec.MenuGroup_id, currRec.MenuID, currRec.OptionNumber = mGrp, mnu, mOpt

        self.fillFormFromcurrRec()

        self.requestMenuReload.emit()   # let listeners know we need a menu reload
    # on_delete_clicked

    # ##########################################
    # ########    Record Status


    ##########################################
    ########    Widget-responding procs

    def copyMenuOption(self):
        cRec = self.currRec()
        tbl = cRec.__table__
        mnuGrp, mnuID, optNum = (cRec.MenuGroup_id, cRec.MenuID, cRec.OptionNumber)

        dlg = self.cEdtMnuItmDlg_CopyMove_MenuItm(mnuGrp, mnuID, optNum, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec_CM_MItm()
        if retval:
            # Create a copy (including relationships)
            new_rec = copy.deepcopy(cRec)

            # Detach the copy from the session
            make_transient(new_rec)

            # Reset primary keys
            new_rec.id = None                       # type: ignore
            new_rec.MenuGroup_id = newMnuID[0]      # type: ignore
            new_rec.MenuID = newMnuID[1]            # type: ignore
            new_rec.OptionNumber = newMnuID[2]      # type: ignore

            ssnmaker = self.ssnmaker()
            assert ssnmaker is not None, "Sessionmaker must be set before touching the database"
            
            Repository(ssnmaker, tbl).add(new_rec)

            if CMChoiceCopy:
                ... # we've done everything we need to do
            else:
                Repository(ssnmaker, tbl).remove(cRec)

                self.initializeRec()
                # preserve MenuGroup, MenuID, OptionNumber
                currRec = self.currRec()
                currRec.MenuGroup_id, currRec.MenuID, currRec.OptionNumber = mnuGrp, mnuID, optNum
            #endif CMChoiceCopy

            self.fillFormFromcurrRec()

            self.requestMenuReload.emit()   # let listeners know we need a menu reload
            
            # announce success
            copyword = 'copied' if CMChoiceCopy else 'moved'
            QMessageBox.information(self,
                self.tr(f"Menu Option {copyword}"),
                self.tr(f"Menu option {mnuGrp}, {mnuID}, {optNum} successfully {copyword} to {newMnuID[0]}, {newMnuID[1]}, {newMnuID[2]}.")
                )

        # #endif retval
        return
    # copyMenuOption
    
# class cWidgetMenuItem
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


class cEditMenu(cSimpleRecordForm):
    _ORMmodel = menuItems
    _ssnmaker = get_cMenu_sessionmaker()
    _formname = 'Edit Menu'
    fieldDefs = {
        '@MenuGroup_id': {'widgetType': cComboBoxFromDict, 'label': 'Menu Group', 'lookupHandler': 'loadMenuWithGroupID', 
            # 'choices': lambda: self.dictmenuGroup(), 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,0), },
        '@MenuID': {'widgetType': cComboBoxFromDict, 'label': 'Menu ID',  'lookupHandler': 'loadMenuWithMenuID', 
            # 'choices': lambda self: self.dictmenus(self.intmenuGroup), 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,0), },
        '+GroupName': {'widgetType': QLineEdit, 'label': 'Menu Group Name', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,2,1,2), },
        'OptionText': {'widgetType': QLineEdit, 'label': 'Menu Name', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,2), },
        '+RmvMenu': {'widgetType': QPushButton, 'label': 'Remove Menu', 'clickedHandler': 'rmvMenu', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,3), },
        '+NewMenuGroup': {'widgetType': QPushButton, 'label': 'New Menu Group', 'clickedHandler': 'createNewMenuGroup', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,4), },
        '+CopyMenu': {'widgetType': QPushButton, 'label': 'Copy/Move Menu', 'clickedHandler': 'copyMenu', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (1,4), },
        '+Commit': {'widgetType': QPushButton, 'label': '\nSave\nChanges\n', 'clickedHandler': 'writeRecord', 
            'page': cQFmConstants.pageFixedTop.value, 'position': (0,5,2,1), },
    }

    # more class constants
    _DFLT_menuGroup: int = -1
    _DFLT_menuID: int = -1
    intmenuGroup:int = _DFLT_menuGroup
    intmenuID:int = _DFLT_menuID
    
    class wdgtmenuITEM(cWidgetMenuItem):
        def __init__(self, menuitmRec, parent = None):
            super().__init__(menuitmRec, parent)
    # wdgtmenuITEM
            
    class cEdtMnuDlgGetNewMenuGroupInfo(QDialog):
        def __init__(self, parent:QWidget|None = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'New Menu Group')

            layoutGroupName = QHBoxLayout()
            lblGroupName = QLabel(self.tr('Group Name'))
            self.lnedtGroupName = QLineEdit('New Group', self)
            layoutGroupName.addWidget(lblGroupName)
            layoutGroupName.addWidget(self.lnedtGroupName)

            layoutGroupInfo = QHBoxLayout()
            lblGroupInfo = QLabel(self.tr('Group Info'))
            self.txtedtGroupInfo = QTextEdit(self)
            layoutGroupInfo.addWidget(lblGroupInfo)
            layoutGroupInfo.addWidget(self.txtedtGroupInfo)

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)            

            layoutMine = QVBoxLayout()
            layoutMine.addLayout(layoutGroupName)
            layoutMine.addLayout(layoutGroupInfo)
            layoutMine.addWidget(dlgButtons)
            
            self.setLayout(layoutMine)
            
        def exec_NewMGInfo(self):
            ret = super().exec()
            # later - prevent lvng if lnedtGroupName blank
            return (
                ret, 
                self.lnedtGroupName.text()         if ret==self.DialogCode.Accepted else None,
                self.txtedtGroupInfo.toPlainText() if ret==self.DialogCode.Accepted else None,
                )
    # cEdtMnuDlgGetNewMenuGroupInfo
    
    class cEdtMnuDlgCopyMoveMenu(QDialog):
        intCMChoiceCopy:int = 10
        intCMChoiceMove:int = 20
        
        def __init__(self, mnuGrp:int, menuID:int, parent:QWidget|None = None):
            super().__init__(parent)
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Copy/Move Menu')

            lblDlgTitle = QLabel(self.tr(f' Copy or Move Menu {menuID}'))
            
            layoutMenuID = QHBoxLayout()
            lblMenuID = QLabel(self.tr('Menu ID'))
            self.combobxMenuID = QComboBox(self)
            
            dictDefinedMenus = MenuRecords().recordsetList(['MenuID'], filter=f'MenuGroup_id={mnuGrp} AND OptionNumber=0')
            definedMenus = {mDict['MenuID'] for mDict in dictDefinedMenus}
            self.combobxMenuID.addItems([str(n) for n in range(256) if n not in definedMenus])
            layoutMenuID.addWidget(lblMenuID)
            layoutMenuID.addWidget(self.combobxMenuID)
            
            visualgrpboxCopyMove = QGroupBox(self.tr("Copy / Move"))
            layoutgrpCopyMove = QHBoxLayout()
            # Create radio buttons
            radioCopy = QRadioButton(self.tr("Copy"))
            radioMove = QRadioButton(self.tr("Move"))
            # Add radio buttons to the layout
            layoutgrpCopyMove.addWidget(radioCopy)
            layoutgrpCopyMove.addWidget(radioMove)
            visualgrpboxCopyMove.setLayout(layoutgrpCopyMove)
            # Create a QButtonGroup for logical grouping
            self.lgclbtngrpCopyMove = QButtonGroup()
            self.lgclbtngrpCopyMove.addButton(radioCopy, id=self.intCMChoiceCopy)
            self.lgclbtngrpCopyMove.addButton(radioMove, id=self.intCMChoiceMove)
            # Add the QGroupBox to the main layout

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)            

            layoutMine = QVBoxLayout()
            layoutMine.addWidget(lblDlgTitle)
            layoutMine.addWidget(visualgrpboxCopyMove)
            layoutMine.addLayout(layoutMenuID)
            layoutMine.addWidget(dlgButtons)
            
            self.setLayout(layoutMine)
            
        def exec_CMMnu(self):
            ret = super().exec()
            copymove = self.lgclbtngrpCopyMove.checkedId()
            return (
                ret, 
                copymove != self.intCMChoiceMove,   # True unless Move checked
                int(self.combobxMenuID.currentText()) if ret==self.DialogCode.Accepted else None,
                )
    # cEdtMnuDlgCopyMoveMenu

    def __init__(self, parent:QWidget|None = None, MainMenuWindow:QWidget|None = None):

        self.MainMenuWindow = MainMenuWindow
        
        # variables unique to this class
        self._menuSOURCE = MenuRecords()
        self.currentMenu: Dict[int, menuItems] = {}
        self.WmenuItm: Any = [None for bNum in range(_NUM_menuBUTTONS)]    # later - build WmenuItm before this loop?

        super().__init__(parent=parent)
        self.layoutForm = self.dictFormLayouts.get('layoutForm')
        assert isinstance(self.layoutForm, cGridWidget), "layoutForm is not a cGridWidget"
        
        # self.fldmenuGroup = self.fieldDefs['@MenuGroup_id'].get('widget') 
        self.fldmenuGroup = self._lookupFrmElements['@MenuGroup_id']
        self.fldmenuGroup.replaceDict(self.dictmenuGroups())    # type: ignore
        self.fldmenuGroupName = self._formWidgets.get('+GroupName') 
        
        self.loadMenu()
    # __init__

    ##########################################
    ########    getters/setters

    def menuSOURCE(self) -> Any:
        return self._menuSOURCE

    ##########################################
    ########    Layout

    def _addActionButtons(self, layoutButtons: QBoxLayout | None = None, layoutHorizontal: bool = True, NavActions: List[Tuple[str, QIcon]] | None = None, CRUDActions: List[Tuple[str, QIcon]] | None = None) -> None:
        # there is no button line on this form
        self.btnCommit = self.fieldDefs['+Commit'].get('widget')
        return
    # _addActionButtons
    
    def _finalizeMainLayout(self, layoutMain: QVBoxLayout, items: List | tuple) -> None:
        self.lblnummenuGroupID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuGroupID.setMaximumSize(20,20)
        self.lblnummenuID:  QLCDNumber = QLCDNumber(3)
        self.lblnummenuID.setMaximumSize(20,20)
        layout = self.FormPage(cQFmConstants.pageFixedTop.value)
        assert layout is not None, "Layout is None"
        layout.addWidget(self.lblnummenuGroupID, 0,1)
        layout.addWidget(self.lblnummenuID, 1,1)

        layoutmainMenu = self.FormPage(0)  # main page
        assert isinstance(layoutmainMenu, QGridLayout), "layoutmainMenu is not a QGridLayout"
        layoutmainMenu.setColumnStretch(0,1)
        layoutmainMenu.setColumnStretch(1,0)
        layoutmainMenu.setColumnStretch(2,1)
        self.layoutmainMenu = layoutmainMenu
        
        bxFrame:List[QFrame] = [QFrame() for _ in range(_NUM_menuBUTTONS)]
        for bNum in range(_NUM_menuBUTTONS):
            bxFrame[bNum].setLineWidth(1)
            bxFrame[bNum].setFrameStyle(QFrame.Shape.Box|QFrame.Shadow.Plain)
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            self.layoutmainMenu.addWidget(bxFrame[bNum],y,x)
            
            self.WmenuItm[bNum] = None      # type: ignore  # later - build WmenuItm before this loop?

        # self.setMinimumWidth(layoutMain.maximumSize().width()+100)
        
        return super()._finalizeMainLayout(layoutMain, items)
    
    ##########################################
    ########    menu and Group dicts

    def dictmenuGroups(self) -> Dict[str, int]:
        # rs = self.menuSOURCE().recordsetList(['MenuGroup_id', 'GroupName'])
        rs = MenuRecords.menuGroupsDict()
        # retDict = {d['GroupName']:d['MenuGroup_id'] for d in rs}
        retDict = rs
        return retDict
    def dictmenus(self, mnuGrp:int) -> Mapping[str, int|None]:
        tbl = self.menuSOURCE()
        rs = tbl.recordsetList(['MenuID', 'OptionText'], f'MenuGroup_id = {mnuGrp} AND OptionNumber = 0')
        retDict = Nochoice | {f"{d['OptionText']} ({d['MenuID']})":d['MenuID'] for d in rs}
        return retDict

    ##########################################
    ########    Display 

    def displayMenu(self):
        from .cMenu import cMenu as cMenuClass

        menuGroup = self.intmenuGroup
        menuID = self.intmenuID
        menuItemRecs = self.currentMenu
        # menuItemRecs.setFilter('OptionNumber=0')
        # menuHdrRec:QSqlRecord = self.movetoutil_findrecwithvalue(menuItemRecs,'OptionNumber',0)
        menuHdrRec:menuItems = menuItemRecs[0]
        
        # set header elements
        self.lblnummenuGroupID.display(menuGroup)
        self.fldmenuGroup.setValue(str(menuGroup)) # type: ignore

        r = Repository(get_cMenu_sessionmaker(), menuGroups).get_by_id(menuGroup)
        # stmt = select(menuGroups.GroupName).where(menuGroups.id == menuGroup)
        # with cMenu_Session() as session:
        #     result = session.execute(stmt)
        #     group_name = result.scalar_one_or_none()
        # GpName = group_name if group_name else ""
        GpName = r.GroupName # type: ignore

        self.fldmenuGroupName.setValue(GpName) # type: ignore
        self.lblnummenuID.display(menuID)
        fldmenuID = self.fieldDefs['@MenuID'].get('widget')        
        fldmenuID.replaceDict(self.dictmenus(menuGroup))  # type: ignore
        fldmenuID.setValue(menuID) # type: ignore
        fldmenuName = self.fieldDefs['OptionText'].get('widget')  # self.fldmenuID.replaceDict(dict(d))
        fldmenuName.setValue(menuHdrRec.OptionText) # type: ignore

        for bNum in range(_NUM_menuBUTTONS):
            y, x = ((bNum % _NUM_menuBTNperCOL)+1, 0 if bNum < _NUM_menuBTNperCOL else 2)
            bIndx = bNum+1
            # mnuItmRc = self.movetoutil_findrecwithvalue(menuItemRecs, 'OptionNumber', bIndx)  # this is safer, but the line below is faster and is same in this case
            mnuItmRc = menuItemRecs.get(bIndx)
            if not mnuItmRc:
                mnuItmRc = menuItems(
                    MenuGroup_id=menuGroup,
                    MenuID=menuID,
                    OptionNumber=bIndx,
                    OptionText = '',
                    Argument = '',
                    PWord = ''
                )
            oldWdg = self.WmenuItm[bNum]
            if oldWdg:
                # remove old widget
                self.layoutmainMenu.removeWidget(oldWdg)
                oldWdg.hide()
                del oldWdg

            self.WmenuItm[bNum] = self.wdgtmenuITEM(mnuItmRc)
            self.WmenuItm[bNum].requestMenuReload.connect(lambda: self.loadMenu(self.intmenuGroup, self.intmenuID))
            if isinstance(self.MainMenuWindow, cMenuClass):
                self.WmenuItm[bNum].requestMenuReload.connect(self.MainMenuWindow.refreshMenu)
            self.layoutmainMenu.addWidget(self.WmenuItm[bNum],y,x) 
        # endfor

        mItmH = self.WmenuItm[0].height()
        mItmW = self.WmenuItm[0].width()
        padW = 70
        multH = 1.5
        # TODO: adjust scroller size based on number of items (do the line below)
        # self.layoutManinMenu_scrollerWidget.setMinimumSize(mItmW*2+10, mItmH)
        assert isinstance(self.layoutForm, cGridWidget), "layoutForm is not a cGridWidget"
        self.layoutForm._scroller.setMinimumSize(mItmW*2+padW, multH*mItmH)     # type: ignore
        
    # displayMenu

    ##########################################
    ########    Create

    def createNewMenuGroup(self):
        dlg = self.cEdtMnuDlgGetNewMenuGroupInfo(self)
        retval, grpName, grpInfo = dlg.exec_NewMGInfo()
        if retval:
            # new menuGroups record
            # create a new menu group
            newrec = menuGroups(
                GroupName=grpName,
                GroupInfo=grpInfo,
            )
            newrec = Repository(get_cMenu_sessionmaker(), menuGroups).add(newrec)
            grppk = newrec.id            
            # with cMenu_Session() as session:
            #     session.add(newrec)
            #     session.commit()
            #     # get the primary key of the new record
            #     grppk = newrec.id            

            # create a default menu
            # newgroupnewmenu_menulist to menuItems
            for rec in newgroupnewmenu_menulist:
                # rec is a dict with keys: OptionNumber, OptionText, Command, Argument, PWord, TopLine, BottomLine
                # create a new record in menuItems
                # TODO: check for existing menu items with same MenuGroup_id and MenuID and OptionNumber?
                # TODO: make sure rec has all required keys
                newmenurec = menuItems(
                    MenuGroup_id=grppk,
                    MenuID=0,  # default menu ID
                    OptionNumber=rec['OptionNumber'],
                    OptionText=rec.get( 'OptionText', ''),
                    Command=rec.get('Command'),
                    Argument=rec.get('Argument' ''),
                    PWord=rec.get('PWord', ''),
                    TopLine=rec.get('TopLine'),
                    BottomLine=rec.get('BottomLine'),
                )
                # save the new record
                Repository(get_cMenu_sessionmaker(), menuItems).add(newmenurec)
                # with cMenu_Session() as session:
                #     session.add(newmenurec)
                #     session.commit()

            self.loadMenu(grppk, 0)
        return

    def copyMenu(self):
        mnuGrp = self.intmenuGroup
        mnuID = self.intmenuID

        dlg = self.cEdtMnuDlgCopyMoveMenu(mnuGrp, mnuID, self)
        retval, CMChoiceCopy, newMnuID = dlg.exec_CMMnu()
        if retval:
            assert isinstance(newMnuID, int) and newMnuID >= 0, "New Menu ID must be a non-negative integer"
            qsFrom = self.currentMenu
            with get_cMenu_session() as session:         
                if CMChoiceCopy:
                    qsTo: Dict[int, menuItems] = {}     # qsTo is technically not used, but being built JIC its needed later
                    for i, orig_rec in qsFrom.items():
                        new_rec = menuItems()
                        for col in menuItems.__table__.columns:
                            name = col.name
                            if name != "id":
                                setattr(new_rec, name, getattr(orig_rec, name))
                        #endfor col in menuItems.__table__.columns

                        new_rec.MenuID = newMnuID
                        session.add(new_rec)
                        qsTo[i] = new_rec     # qsTo is technically not used, but being built JIC its needed later
                    #endfor i, orig_rec in qsFrom.items()
                else:
                    # Move the menu items to the new menu ID
                    for i, orig_rec in qsFrom.items():
                        # Update the MenuID of the original record
                        orig_rec.MenuID = newMnuID
                        session.merge(orig_rec)
                    #endfor i, orig_rec in qsFrom.items()
                #endif CMChoiceCopy
                
                session.commit()                # commit the changes
                
                self.loadMenu(mnuGrp, newMnuID)
                
            #endwith cMenu_Session() as session:
        #endif retval

        return
    # copyMenu
        
    ##########################################
    ########    Read

    @Slot()
    def loadMenuWithGroupID(self, menuGroup:int):
        # menuGroup = self.fldmenuGroup.Value()  # type: ignore
        menuID = self._DFLT_menuID
        if menuGroup is None or menuID is None:
            return
        self.loadMenu(int(menuGroup), int(menuID))
    # loadMenuWithGroupID
    @Slot()
    def loadMenuWithMenuID(self, menuID:int):
        # menuID = self.fldmenuID.Value()        # type: ignore
        if menuID is None:
            return
        self.loadMenu(self.intmenuGroup, int(menuID))
    # loadMenuWithMenuID
    @Slot(int, int)
    def loadMenu(self, menuGroup: int = _DFLT_menuGroup, menuID: int = _DFLT_menuID):
        SRC = self._menuSOURCE
        if menuGroup==self._DFLT_menuGroup:
            dfltMenuGroup = SRC.dfltMenuGroup()
            if dfltMenuGroup is None:
                raise ValueError("Default menu group not found.")
            menuGroup = dfltMenuGroup
        if menuID==self._DFLT_menuID:
            dfltMenuID = SRC.dfltMenuID_forGroup(menuGroup)
            if dfltMenuID is None:
                raise ValueError(f"Default menu ID for group {menuGroup} not found.")
            menuID = dfltMenuID

        self.intmenuGroup = menuGroup
        self.intmenuID = menuID
        
        if SRC.menuExist(menuGroup, menuID):
            self.currentMenu = SRC.menuDBRecs(menuGroup, menuID)
            # self.currRec = self.movetoutil_findrecwithvalue(self.currentMenu, 'OptionNumber', 0)
            self.setcurrRec(self.currentMenu[0])  # am I safe in assuming existence?
            self.setDirty(False)       # should this be in displayMenu ?
            self.displayMenu()
        else:
            # menu doesn't exist; say so
            msg = QMessageBox(self)
            msg.setWindowTitle('Menu Doesn\'t Exist')
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.setText(f'Menu {menuID} doesn\'t exist!')
            msg.open()
    # loadMenu

    ##########################################
    ########    Update

    @Slot(Any)   #type: ignore
    # def changeField(self, wdgt:cQFmFldWidg) -> bool:
    def changeField(self, wdgt, dbField, wdgt_value):

        cRec = self.currRec()

        super().changeField(wdgt, dbField, wdgt_value)
        
        if wdgt_value or isinstance(wdgt_value,bool):
            if dbField != '+GroupName':  # GroupName belongs to cRec.MenuGroup; persist only at final write
                assert cRec is not None, "Current record is None"
                cRec.setValue(str(dbField), wdgt_value)
            wdgt.setDirty(True)
        
            return True
        else:
            return False
        # endif wdgt_value
    # changeField
    
    # def changeInternalVarField(self, wdgt):
    def changeInternalVarField(self, wdgt, intVarField, wdgt_value):
        # '+RmvMenu': {'widgetType': QPushButton, 'label': 'Remove Menu', 'clickedHandler': 'rmvMenu', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (1,3), },
        # '+NewMenuGroup': {'widgetType': QPushButton, 'label': 'New Menu Group', 'clickedHandler': 'createNewMenuGroup', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (0,4), },
        # '+CopyMenu': {'widgetType': QPushButton, 'label': 'Copy/Move Menu', 'clickedHandler': 'copyMenu', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (1,4), },
        # '+Commit': {'widgetType': QPushButton, 'label': 'Save Changes', 'clickedHandler': 'writeRecord', 
        #     'page': cQFmConstants.pageFixedTop.value, 'position': (1,5,2,1), },
        # assert isinstance(wdgt, cQFmFldWidg), "wdgt is not a cQFmFldWidg"
        # intVarField = wdgt.modelField()
        _internalVarFields = {
            '+RmvMenu': self.rmvMenu, 
            '+NewMenuGroup': self.createNewMenuGroup, 
            '+CopyMenu': self.copyMenu, 
            '+Commit': self.writeRecord,
            '+GroupName': lambda: None,  # GroupName belongs to cRec.MenuGroup; persist only at final write
            }
                
        if intVarField in _internalVarFields:
            _internalVarFields[intVarField]()
        # else:
        #     no need to raise error
        #     raise ValueError(f"Unknown internal variable field: {intVarField}")
        # endif
    # changeInternalVarField

    @Slot()
    def writeRecord(self):
        if not self.isDirty():
            return
        
        cRec = self.currRec()
        
        # check other traps later
        
        # fldmenuGroupName = self.fieldDefs['+GroupName'].get('widget')  # type: ignore
        fldmenuGroupName = self._formWidgets['+GroupName']
        
        if fldmenuGroupName.isDirty():  # type: ignore
            # update the menu group name in menuGroups table
            groupRec = Repository(get_cMenu_sessionmaker(), menuGroups).get_by_id(self.intmenuGroup)
            if groupRec is None:
                print("Menu group not found:", self.intmenuGroup)
                return
            groupRec.GroupName = str(fldmenuGroupName.Value())  # type: ignore
            Repository(get_cMenu_sessionmaker(), menuGroups).update(groupRec)
            # grpstmt = select(menuGroups).where(menuGroups.id == self.intmenuGroup)
            # with cMenu_Session() as session:
            #     groupRec = session.execute(grpstmt).scalar_one_or_none()
            #     if groupRec is None:
            #         print("Menu group not found:", self.intmenuGroup)
            #         return
            #     # update the group name
            #     groupRec.GroupName = str(fldmenuGroupName.Value())  # type: ignore
            #     session.merge(groupRec)
            #     session.commit()
            # #endwith cMenu_Session() as session:
        #endif self.isWdgtDirty(self.fldmenuGroupName)

        if cRec is not None:
            Repository(get_cMenu_sessionmaker(), menuItems).update(cRec)
            # with cMenu_Session() as session:
            #     session.merge(cRec)
            #     session.commit()

        self.setDirty(False)
    # writeRecord

    ##########################################
    ########    Delete

    @Slot()
    def rmvMenu(self):
        
        pleaseWriteMe('Remove Menu', parent=self)
        return
        
        ##### old code below #####
        # (mGrp, mnu, mOpt) = (self.currRec().MenuGroup, self.currRec().MenuID, self.currRec().OptionNumber)
        
        # # verify delete
        
        # # remove from db
        # if self.currRec().pk:
        #     self.currRec().delete()
        
        # # replace with an "next" record
        # self.setcurrRec(menuItems_QT(
        #     MenuGroup = mGrp,
        #     MenuID = mnu,
        #     OptionNumber = mOpt,
        #     ))
    # rmvMenu

    ##########################################
    ########    object status

    ##########################################
    ########    Widget-responding procs

# cEditMenu

#############################################
#############################################
#############################################


class OpenTable(QWidget):
    
    class cOpnTblDlgGetTable(QDialog):
        _tableListSQL:str = 'PRAGMA table_list;'
        
        def __init__(self, parent:QWidget|None = None):
            super().__init__(parent)
            
            app_sessionmaker = cTools_apphooks().get_app_sessionmaker()
            
            self.setWindowModality(Qt.WindowModality.WindowModal)
            self.setWindowTitle(parent.windowTitle() if parent else 'Choose Table')

            layoutTableName = QHBoxLayout()
            lblTableName = QLabel(self.tr('Table to Show'))
            self.combobxTableName = QComboBox(self)
            self.combobxTableName.addItems(self.TableList(app_sessionmaker))
            layoutTableName.addWidget(lblTableName)
            layoutTableName.addWidget(self.combobxTableName)

            dlgButtons = QDialogButtonBox(
                QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel,
                Qt.Orientation.Horizontal,
                )
            dlgButtons.accepted.connect(self.accept)
            dlgButtons.rejected.connect(self.reject)            

            layoutMine = QVBoxLayout()
            layoutMine.addLayout(layoutTableName)
            layoutMine.addWidget(dlgButtons)
            
            self.setLayout(layoutMine)

        def TableList(self, app_sessionmaker) -> List:
            
            db:Engine = app_sessionmaker().get_bind()
            
            qmodel = SQLAlchemySQLQueryModel(self._tableListSQL, db)
            
            colIdx = qmodel.colIndex('name')
            if colIdx < 0:
                # no 'name' column found
                # raise ValueError("No 'name' column found in the table list query result.")
                return []

            # retList = [qmodel.record(n)[colIdx] for n in range(qmodel.rowCount())]
            retList = [qmodel.data(qmodel.index(n, colIdx)) for n in range(qmodel.rowCount())]
            return retList

        def exec_DlgGetTbl(self):
            ret = super().exec()
            # later - prevent lvng if lnedtGroupName blank
            return (
                ret, 
                self.combobxTableName.currentText()    if ret==self.DialogCode.Accepted else None,
                )
    
    def __init__(self, tbl:str|None = None, parent:QWidget|None = None):
        super().__init__(parent)
        
        # font = QFont()
        # font.setPointSize(12)
        # self.setFont(font)
    
        app_sessionmaker = cTools_apphooks().get_app_sessionmaker()
        assert app_sessionmaker is not None, "app_sessionmaker must be provided"
        db:Engine=app_sessionmaker().get_bind()
        
        if not tbl:
            # get tbl name
                # use self._tableListSQL
            # read all table names
            # present and select
            tbl = self.chooseTable()
        
        # for testing ...
        # tbl = 'incShip_hbl'
        
        # read into model
        # verify tbl exists
        # error, rows, colNames = (None, [], [])
        # error, rows, colNames = self.getTable(tbl)
        # if error:
        #     raise error
        
        # tblWidget = self.tableWidget(rows, colNames)
        tblWidget = self.tableWidget(tbl, db)
        self.model = tblWidget.model()
        # bring all rows in so rowCount will be correct
        # while tblWidget.model().canFetchMore():
        #     tblWidget.model().fetchMore()
        rows = tblWidget.model().rowCount()
        colNames = [tblWidget.model().headerData(n, Qt.Orientation.Horizontal) for n in range(tblWidget.model().columnCount())]
        # present TableView

        # save incoming for future use if needed
        self.rows = rows
        self.colNames = colNames

        self.layoutForm = QVBoxLayout(self)

        #TODO: make Title the name of the table        
        #TODO: note on screen that this form is RO        
        # Form Header Layout
        self.layoutFormHdr = QVBoxLayout()
        self.lblFormName = cQFmNameLabel()
        self.lblFormName.setText(self.tr('Table'))
        self.setWindowTitle(self.tr('Table'))
        self.layoutFormHdr.addWidget(self.lblFormName)
        
        self.layoutFormTableDescription = QFormLayout()
        lblnRecs = QLabel()
        lblnRecs.setText(f'{rows}')
        lblcolNames = QLabel()
        lblcolNames.setText(str(colNames))
        self.layoutFormTableDescription.addRow('rows:', lblnRecs)
        self.layoutFormTableDescription.addRow('cols:', lblcolNames)

        # main area for displaying SQL
        self.layoutFormMain = QVBoxLayout()
        self.layoutFormMain.addWidget(tblWidget)
        
        # nope - this is RO
        # # Add a add row button
        # addrow_button = QPushButton("Add Row")
        # addrow_button.clicked.connect(lambda: self.addRow())
        
        # # Add a save button
        # save_button = QPushButton("Save Changes")
        # save_button.clicked.connect(lambda: self.model.save_changes() or print("Saved!"))    # type: ignore
        
        # layoutButtons = QHBoxLayout()
        # layoutButtons.addWidget(addrow_button)
        # layoutButtons.addWidget(save_button)
        
        self.layoutForm.addLayout(self.layoutFormHdr)
        self.layoutForm.addLayout(self.layoutFormTableDescription)
        self.layoutForm.addLayout(self.layoutFormMain)
        # self.layoutForm.addLayout(layoutButtons)
        
    def chooseTable(self) -> str|None:
        dlg = self.cOpnTblDlgGetTable(self)
        retval, tblName = dlg.exec_DlgGetTbl()
        return tblName if retval == QDialog.DialogCode.Accepted else None
            

    def getTable(self, tblName:str): # -> Tuple[Exception|None, List[Dict[str, Any]], List[str]|str]:
        pleaseWriteMe('fix getTable in class OpenTable', parent=self)
        # inputSQL:str = f'SELECT * FROM {tblName}'
        # # inputSQL:str = f'SELECT * FROM %(tblName)s'
        # sqlerr = None
        # with db.connection.cursor() as djngocursor:
        #     try:
        #         djngocursor.execute(inputSQL)
        #         # djngocursor.execute(inputSQL, [tblName])
        #     except Exception as err:
        #         sqlerr = err
        #     colNames = []
        #     rows = []
        #     if not sqlerr:
        #         if djngocursor.description:
        #             colNames = [col[0] for col in djngocursor.description]
        #             rows = dictfetchall(djngocursor)
        #         else:
        #             colNames = 'NO RECORDS RETURNED; ' + str(djngocursor.rowcount) + ' records affected'
        #             rows = []
        #         #endif cursor.description
        #     else:  
        #         # nothing to do
        #         ...
        #     #endif not sqlerr
        # #end with
        
        # return (sqlerr, rows, colNames)

    # def tableWidget(self, rows:List[Dict[str, Any]], colNames:str|List[str]) -> QTableView:
    def tableWidget(self, tbl:str|None, db:Engine) -> QTableView:
        sqlstat = f"SELECT * FROM {tbl}" if tbl else "SELECT * FROM sqlite_master WHERE type='table';"
        resultModel = SQLAlchemySQLQueryModel(sqlstat, db, self.parent())
        resultTable = QTableView()
        # resultTable.verticalHeader().setHidden(True)
        header = resultTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        # Apply stylesheet to control text wrapping
        resultTable.setStyleSheet("""
        QHeaderView::section {
            padding: 5px;
            font-size: 12px;
            text-align: center;
            white-space: normal;  /* Allow text to wrap */
        }
        """)
        resultTable.setModel(resultModel)
        
        return resultTable
        
    def addRow(self):
        self.model.insertRow(self.model.rowCount())


#############################################
#############################################

class loadExternalWebPage():
    def __init__(self, url:str|None, parent:QWidget|None = None):
        if url:
            self.reloadPage(url)
    # __init__
    
    def reloadPage(self, url:str):
        webbrowser.open_new_tab(url)
    # reloadPage


#############################################
#############################################
#############################################

