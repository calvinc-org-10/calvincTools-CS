from . import (MENUCOMMANDDICTIONARY, MENUCOMMAND, )


initial_menus = {}

# self, menuID: str, menuName: str, menuItems:Dict[int,Dict]):
# {'keys': {'MenuGroup': 1, 'MenuID': 0, 'OptionNumber': 0}, 
#     'values': {etc}}
initial_menus['new.super.menugroup.newmenu'] = [
{'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': 'Default', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'OptionNumber': 11,
    'OptionText': 'Edit Menu', 'Command': MENUCOMMAND.EditMenu, 'Argument': '', 'PWord': '', },
{'OptionNumber': 19,
    'OptionText': 'Change Password', 'Command': MENUCOMMAND.ChangePW, 'Argument': '', 'PWord': '', },
{'OptionNumber': 20,
    'OptionText': 'Go Away!', 'Command': MENUCOMMAND.ExitApplication, 'Argument': '', 'PWord': '', },
]

initial_menus['new.ordinary.menugroup.newmenu'] = [
{'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': 'Default', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'OptionNumber': 19,
    'OptionText': 'Change Password', 'Command': MENUCOMMAND.ChangePW, 'Argument': '', 'PWord': '', },
{'OptionNumber': 20,
    'OptionText': 'Go Away!', 'Command': MENUCOMMAND.ExitApplication, 'Argument': '', 'PWord': '', },
]

initial_menus['existing.group.newmenu'] = [
{'OptionNumber': 0,
    'OptionText': 'New Menu', 'Command': None, 'Argument': '', 'PWord': '', 'TopLine': 1, 'BottomLine': 1, },
{'OptionNumber': 20,
    'OptionText': 'Return to Main Menu', 'Command': MENUCOMMAND.LoadMenu, 'Argument': '0', 'PWord': '', },
]

    