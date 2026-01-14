from typing import (Any, Dict, List, Optional, )

from sqlalchemy import Row, RowMapping, Select, Table, select, text

from .menucommand_constants import (MENUCOMMANDS, COMMANDNUMBER, )
from .database import get_cMenu_session, get_cMenu_sessionmaker

from .utils import (retListofQSQLRecord, recordsetList, select_with_join_excluding, )

# self, menuID: str, menuName: str, menuItems:Dict[int,Dict]):
# {'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 0}, 
#     'values': {etc}}
initmenu_menulist = [
{'MenuID': -1, 'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': 'Default', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'MenuID': -1, 'OptionNumber': 11,
    'OptionText': 'Edit Menu', 'Command': COMMANDNUMBER.EditMenu, 'Argument': '', 'PWord': '', },
{'MenuID': -1, 'OptionNumber': 19,
    'OptionText': 'Change Password', 'Command': COMMANDNUMBER.ChangePW, 'Argument': '', 'PWord': '', },
{'MenuID': -1, 'OptionNumber': 20,
    'OptionText': 'Go Away!', 'Command': COMMANDNUMBER.ExitApplication, 'Argument': '', 'PWord': '', },
]

newgroupnewmenu_menulist = [
{'MenuID': 0, 'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': 'Default', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'MenuID': 0, 'OptionNumber': 19,
    'OptionText': 'Change Password', 'Command': COMMANDNUMBER.ChangePW, 'Argument': '', 'PWord': '', },
{'MenuID': 0, 'OptionNumber': 20,
    'OptionText': 'Go Away!', 'Command': COMMANDNUMBER.ExitApplication, 'Argument': '', 'PWord': '', },
]

newmenu_menulist = [
{'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'OptionNumber': 20,
    'OptionText': 'Return to Main Menu', 'Command': COMMANDNUMBER.LoadMenu, 'Argument': '0', 'PWord': '', },
]


from .models import menuGroups, menuItems

class MenuRecords:
    """A class for managing menu items in the database."""
    # all methods of this class are classmethods
    
    _tbl = menuItems
    _tblGroup = menuGroups

    # def __init__(self):
    #     self.session = None

    # def __enter__(self):
    #     self.session = get_cMenu_session
    #     return self
    
    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     if self.session:
    #         if exc_type is None:
    #             self.session.commit()
    #         else:
    #             self.session.rollback()
    #         self.session.close()

    @classmethod
    def create(cls, persist:bool = True, **kwargs) -> menuItems:
        """Create a new menu item record."""
        new_item = cls._tbl(**kwargs)
        if persist:
            with get_cMenu_session() as session:
                session.add(new_item)
                session.commit()
        #endif
        return new_item
    
    @classmethod
    def get(cls, record_id: int) -> Optional[menuItems]:
        """Get a menu item by its primary key."""
        with get_cMenu_session() as session:
            return session.get(cls._tbl, record_id)
        
    
    @classmethod
    def update(cls, record_id: int, **kwargs) -> Optional[menuItems]:
        """Update an existing menu item record."""
        with get_cMenu_session() as session:
            item = session.get(cls._tbl, record_id)
            if item:
                for key, value in kwargs.items():
                    setattr(item, key, value)
                session.commit()
                return item
        return None
    
    @classmethod
    def delete(cls, record_id: int) -> bool:
        """Delete a menu item record."""
        with get_cMenu_session() as session:
            item = session.get(cls._tbl, record_id)
            if item:
                session.delete(item)
                session.commit()
                return True
        return False
    
    @classmethod
    def menuAttr(cls, mGroup: int, mID: int, Opt: int, AttrName: str) -> Any:
        """Get a specific attribute from a menu item."""
        stmt = select(getattr(cls._tbl, AttrName)).where(
            cls._tbl.MenuGroup_id == mGroup,
            cls._tbl.MenuID == mID,
            cls._tbl.OptionNumber == Opt
        )
        with get_cMenu_session() as session:
            return session.scalar(stmt)
    
    @classmethod
    def minMenuID_forGroup(cls, mGroup: int) -> Optional[int]:
        """
        Returns the minimum MenuID for the given MenuGroup.
        """
        stmt = select(cls._tbl.MenuID).where(
            cls._tbl.MenuGroup_id == mGroup,
            cls._tbl.OptionNumber == 0
        ).order_by(cls._tbl.MenuID.asc())
        with get_cMenu_session() as session:
            retval = session.scalars(stmt).first()
        return retval

    @classmethod
    def dfltMenuID_forGroup(cls, mGroup:int) -> Optional[int]:
        stmt = select(cls._tbl.MenuID).where(
            cls._tbl.MenuGroup_id == mGroup,
            cls._tbl.Argument.ilike('default'),
            cls._tbl.OptionNumber == 0
            )
        with get_cMenu_session() as session:
            retval = session.scalar(stmt)
        if retval is None:
            # If no record found, we need to find the minimum MenuID for this group
            retval = cls.minMenuID_forGroup(mGroup)
        return retval

    @classmethod
    def dfltMenuGroup(cls) -> Optional[int]:
        """
        Returns the minimum MenuGroup.
        """
        stmt = select(cls._tbl.MenuGroup_id).order_by(cls._tbl.MenuGroup_id.asc())
        with get_cMenu_session() as session:
            retval = session.scalars(stmt).first()
        return retval

    @classmethod
    def menuDict(cls, mGroup:int, mID:int) ->  Dict[int,Dict[str, Any]]:
        # use selectjoin
        stmt = (
            select(*cls._tbl.__table__.columns)
            .join(cls._tblGroup, cls._tbl.MenuGroup_id == cls._tblGroup.id)
            .where(
                cls._tbl.MenuGroup_id == mGroup,
                cls._tbl.MenuID == mID
                )
            )
        with get_cMenu_session() as session:
            result = session.execute(stmt).mappings()
            # Convert the result to a dictionary with OptionNumber as keys
            # and dictionaries of field values as values
            # Note: 'rec' is a RowMapping, so we can access fields by name
            retDict = { row['OptionNumber']: dict(row) for row in result }
        return retDict

    @classmethod
    def menuGroupsDict(cls) -> Dict[str, int]:
        """Return a dictionary mapping GroupName to id for all menu groups."""
        # TODO: generalize this to work with any table (return a dict of {id:record})
        listmenuGroups = recordsetList(menuGroups, retFlds=['GroupName', 'id'], ssnmaker=get_cMenu_sessionmaker(), orderby='GroupName')
        # stmt = select(menuGroups.GroupName, menuGroups.id).select_from(menuGroups).order_by(menuGroups.GroupName)
        # with get_cMenu_session() as session:
        #     retDict = {row.GroupName: row.id for row in session.execute(stmt).all()}
        retDict = {row['GroupName']: row['id'] for row in listmenuGroups}
        return retDict

    @classmethod
    def menuListDict(cls, mGroup:int) ->  Dict[str, int]:
        listmenuItems = recordsetList(menuItems, 
            retFlds=['OptionText', 'MenuID'], 
            where=f'OptionNumber=0 AND MenuGroup_id={mGroup}', 
            ssnmaker=get_cMenu_sessionmaker(), 
            orderby='MenuID'
            )
        retDict = {row['OptionText']: row['MenuID'] for row in listmenuItems}
        return retDict
    # menuListDict
   
    @classmethod
    # def menuDBRecs(self, mGroup:int, mID:int) ->  QuerySet:
    def menuDBRecs(cls, mGroup:int, mID:int) ->  Dict[int, menuItems]:
        # use selectjoin
        stmt = (
            select(cls._tbl)
            .join(cls._tblGroup, cls._tbl.MenuGroup_id == cls._tblGroup.id)
            .where(
                cls._tbl.MenuGroup_id == mGroup,
                cls._tbl.MenuID == mID
            )
        )
        with get_cMenu_session() as session:
            result = session.execute(stmt).scalars()
            # Convert the result to a dictionary with OptionNumber as keys
            # and the menuItems objects as values
            retDict = { rec.OptionNumber: rec for rec in result }
        return retDict

    @classmethod
    def menuExist(cls, mGroup:int, mID:int) ->  bool:
        stmt = select(cls._tbl).where(
            cls._tbl.MenuGroup_id == mGroup,
            cls._tbl.MenuID == mID,
            cls._tbl.OptionNumber == 0
        )
        with get_cMenu_session() as session:
            result = session.execute(stmt).first()
        # If the result is None, the menu does not exist
        # If the result is a Row or RowMapping, the menu exists
        return (result is not None)

    # TODO: generalize this, mebbe to a new class
    @classmethod
    def recordsetList(cls, retFlds:int|List[str] = retListofQSQLRecord, filter:Optional[str] = None) -> List:
        #TODO: deprecate this method in favor of using recordsetList utility function directly
        stmt:Select = select_with_join_excluding(cls._tbl.__table__, cls._tblGroup.__table__, (cls._tbl.MenuGroup_id == cls._tblGroup.id), ['id'])
        if retFlds == '*' or (isinstance(retFlds,List) and retFlds[0]=='*') or retFlds == retListofQSQLRecord:
            stmt = stmt
        elif isinstance(retFlds, List):
            # Filter the existing selected columns by name
            filtered_cols = [
                col for col in stmt.selected_columns
                if col.name in retFlds
            ]

            # Apply with_only_columns
            stmt = stmt.with_only_columns(*filtered_cols)
        else:
            stmt = stmt
        #endif retFlds
        if filter:
            stmt = stmt.where(text(filter))
        #endif filter

        with get_cMenu_session() as session:
            records = session.execute(stmt)
            retList = list(records.mappings())

        return retList

    #enddef recordsetList

    @classmethod
    def newgroupnewmenuDict(cls, mGroup:int, mID:int) ->  List[Dict]:
        return newgroupnewmenu_menulist
    @classmethod
    def newmenuDict(cls, mGroup:int, mID:int) ->  List[Dict]:
        return newmenu_menulist
    