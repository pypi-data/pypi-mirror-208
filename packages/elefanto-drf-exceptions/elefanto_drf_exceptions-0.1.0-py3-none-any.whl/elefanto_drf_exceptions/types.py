from dataclasses import dataclass
from typing import Optional, List

from drf_standardized_errors.types import ErrorType


@dataclass
class Error:
    code: str
    message: str
    field: Optional[str]


@dataclass
class ErrorResponse:
    type: ErrorType
    errors: List[Error]
