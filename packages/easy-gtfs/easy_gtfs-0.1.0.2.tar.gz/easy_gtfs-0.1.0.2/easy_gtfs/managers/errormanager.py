
class ErrorManager():
    def __init__(self, silent_errors: bool = False) -> None:
        self.silent_errors: bool = silent_errors
        self._errors: list = []

    
    def set_silent_errors(self, silent_errors: bool) -> bool:
        if isinstance(silent_errors, bool):
            self.silent_errors = silent_errors
            return True
        
        return False
    

    def get_silent_errors(self) -> bool:
        return self.silent_errors
    

    def errors(self) -> list:
        return self._errors


    def clear(self) -> bool:
        self._errors = []
        return True

    
    def add_error(self, error) -> bool:
        self._errors.append(error)
        return True