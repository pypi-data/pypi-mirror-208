# DRF Standardized Errors

Standardize your [DRF](https://www.django-rest-framework.org/) API error responses.

By default, the package will convert all API error responses (4xx and 5xx) to a standardized format:
```json
{
  "type": "validation_error",
  "errors": [
    {
      "code": "required",
      "message": "This field is required.",
      "field": "name"
    },
    {
      "code": "max_length",
      "message": "Ensure this value has at most 100 characters.",
      "field": "title"
    }
  ]
}
```
```json
{
  "type": "client_error",
  "errors": [
    {
      "code": "authentication_failed",
      "message": "Incorrect authentication credentials.",
      "field": null
    }
  ]
}
```
```json
{
  "type": "server_error",
  "errors": [
    {
      "code": "error",
      "message": "A server error occurred.",
      "field": null
    }
  ]
}
```


## Features

- Supports nested serializers and ListSerializer errors
- Plays nicely with error monitoring tools (like Sentry, ...)


## Requirements

- python >= 3.8
- Django >= 3.2
- DRF >= 3.12


## Quickstart

Install with `pip`
```shell
pip install elefanto-drf-exceptions
```

Add drf-standardized-errors to your installed apps
```python
INSTALLED_APPS = [
    # other apps
    "elefanto_drf_exceptions",
]
```

Register the exception handler
```python
REST_FRAMEWORK = {
    # other settings
    "EXCEPTION_HANDLER": "elefanto_drf_exceptions.handler.exception_handler"
}
```

Register the error formatter
```python
DRF_STANDARDIZED_ERRORS = {
    "EXCEPTION_FORMATTER_CLASS": "elefanto_drf_exceptions.formatter.ElefantoExceptionFormatter",
}

```

### Notes
Standardized error responses when `DEBUG=True` for **unhandled exceptions** are disabled by default. That is
to allow you to get more information out of the traceback. You can enable standardized errors instead with:
```python
DRF_STANDARDIZED_ERRORS = {
    # other settings
    "ENABLE_IN_DEBUG_FOR_UNHANDLED_EXCEPTIONS": True
}
```

## Integration with DRF spectacular
If you plan to use [drf-spectacular](https://github.com/tfranzel/drf-spectacular) to generate an OpenAPI 3 schema,
install with `pip install drf-standardized-errors[openapi]`. After that, check the [doc page](https://drf-standardized-errors.readthedocs.io/en/latest/openapi.html)
for configuring the integration.

## Links

This project depends on [drf-standardized-errors](https://github.com/ghazi-git/drf-standardized-errors). For more information go to links below

- Documentation: https://drf-standardized-errors.readthedocs.io/en/latest/
- Changelog: https://github.com/ghazi-git/drf-standardized-errors/releases
- Code & issues: https://github.com/ghazi-git/drf-standardized-errors
- PyPI: https://pypi.org/project/drf-standardized-errors/
