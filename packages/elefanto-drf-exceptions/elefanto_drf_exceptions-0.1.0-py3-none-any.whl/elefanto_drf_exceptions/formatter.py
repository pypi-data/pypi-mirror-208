from typing import List, Union

from drf_standardized_errors.formatter import ExceptionFormatter
from drf_standardized_errors.settings import package_settings
from drf_standardized_errors.types import ErrorType
from rest_framework import exceptions

from elefanto_drf_exceptions.types import ErrorResponse, Error


def flatten_errors(
    detail: Union[list, dict, exceptions.ErrorDetail], attr=None, index=None
) -> List[Error]:
    """
    convert this:
    {
        "password": [
            ErrorDetail("This password is too short.", code="password_too_short"),
            ErrorDetail("The password is too similar to the username.", code="password_too_similar"),
        ],
        "linked_accounts" [
            {},
            {"email": [ErrorDetail("Enter a valid email address.", code="invalid")]},
        ]
    }
    to:
    {
        "type": "validation_error",
        "errors": [
            {
                "code": "password_too_short",
                "detail": "This password is too short.",
                "attr": "password"
            },
            {
                "code": "password_too_similar",
                "detail": "The password is too similar to the username.",
                "attr": "password"
            },
            {
                "code": "invalid",
                "detail": "Enter a valid email address.",
                "attr": "linked_accounts.1.email"
            }
        ]
    }
    """

    if not detail:
        return []
    elif isinstance(detail, list):
        first_item, *rest = detail
        if not isinstance(first_item, exceptions.ErrorDetail):
            index = 0 if index is None else index + 1
            if attr:
                new_attr = f"{attr}{package_settings.NESTED_FIELD_SEPARATOR}{index}"
            else:
                new_attr = str(index)
            return flatten_errors(first_item, new_attr, index) + flatten_errors(
                rest, attr, index
            )
        else:
            return flatten_errors(first_item, attr, index) + flatten_errors(
                rest, attr, index
            )
    elif isinstance(detail, dict):
        (key, value), *rest = list(detail.items())
        if attr:
            key = f"{attr}{package_settings.NESTED_FIELD_SEPARATOR}{key}"
        return flatten_errors(value, key) + flatten_errors(dict(rest), attr)
    else:
        return [Error(detail.code, str(detail), attr)]


class ElefantoExceptionFormatter(ExceptionFormatter):
    def get_errors(self) -> List[Error]:
        """
        Account for validation errors in nested serializers by returning a list
        of errors instead of a nested dict
        """
        return flatten_errors(self.exc.detail)

    def get_error_response(
        self, error_type: ErrorType, errors: List[Error]
    ) -> ErrorResponse:
        return ErrorResponse(error_type, errors)
