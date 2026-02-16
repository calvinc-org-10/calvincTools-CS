

def pleaseWriteMe(addlmessage, parent):
    """Display a message box indicating that a feature needs to be implemented.
    
    Args:
        parent: Parent widget for the message box.
        addlmessage: Additional message to display to the user.
    """
    # handled in calvinprocs.js in CalvinTools web app
    pass

# TODO: pass in YesAction, NoAction
def areYouSure(parent, title:str, 
        areYouSureQuestion:str, 
        answerChoices = None,
        dfltAnswer = None,
        ) -> None:
    """Display a confirmation dialog and return the user's choice.
    
    Args:
        parent (QWidget): Parent widget for the message box.
        title (str): Title of the message box.
        areYouSureQuestion (str): Question to ask the user.
        answerChoices (QMessageBox.StandardButton, optional): Available answer buttons.
            Defaults to Yes|No.
        dfltAnswer (QMessageBox.StandardButton, optional): Default button.
            Defaults to No.
    
    Returns:
        QMessageBox.StandardButton: The button that was clicked.
    """
    # handled in cTools_common.html in CalvinTools web app
    pass

