"""
    Some utility functions used all around the files
"""

import variables
from managers.errormanager import ErrorManager



def get_error_manager() -> ErrorManager:
    """
        Returns the current error manager, if none is set it will create one.

        :return [ErrorManager]
    """

    if variables.ERRORMANAGER == None:
        return init_error_manager()
    
    return variables.ERRORMANAGER



def init_error_manager(silent_errors: bool = False) -> ErrorManager:
    """
        Creates a new error manager.

        :param silent_errors [bool] -- Whether or not it should raise errors which are not critical

        :return [ErrorManager]
    """

    new_error_manager = ErrorManager(silent_errors=silent_errors)
    new_error_manager.clear()

    return new_error_manager



def set_error_manager(error_manager: ErrorManager) -> bool:
    """
        Sets the package error manager to the manager you passed.

        :param error_manager [ErrorManager] -- An ErrorManager class object

        :return [bool] -- True on success, False on fail
    """

    if isinstance(error_manager, ErrorManager):
        variables.ERRORMANAGER = error_manager
        return True
    
    return False

