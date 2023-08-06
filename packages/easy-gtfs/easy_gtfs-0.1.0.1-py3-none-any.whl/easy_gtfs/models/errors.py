
from enum import Enum
from pydantic import BaseModel


class ErrorTypes(Enum):
    AgencyError: int = 0
    AgencyErrorDuplicateID: int = 1
    AgencyErrorInvalidAgency: int = 2


class AgencyError(BaseModel):
    caller: str = "Agency"
    name: str = "AgencyError"
    error_type: ErrorTypes = ErrorTypes.AgencyError
    message: str
    values: list