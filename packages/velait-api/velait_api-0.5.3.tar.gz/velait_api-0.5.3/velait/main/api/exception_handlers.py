from django.conf import settings
from rest_framework.views import exception_handler
from django.core.exceptions import ValidationError

from velait.main.exceptions import VelaitError
from velait.main.api.responses import APIResponse


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    response_exists = response is not None

    if not response_exists:
        if isinstance(exc, ValidationError):
            errors = [
                VelaitError(name=error.code, description="\n".join(error.messages))
                for error in exc.error_list
            ]
        else:
            if settings.DEBUG:
                raise exc

            errors = [
                VelaitError(
                    name=getattr(exc, 'name', "Unknown error"),
                    description=getattr(exc, 'description', "Unknown error"),
                )
            ]

        response = APIResponse(data=None, status=400)
    else:
        if isinstance(response.data, dict):
            errors = [
                VelaitError(name=error_name, description=error_description)
                for error_name, error_description in response.data.items()
            ]
        else:
            errors = response.data

    return APIResponse(
        data=None,
        status=response.status_code,
        template_name=response.template_name,
        headers=response.headers,
        exception=response.exception,
        content_type=response.content_type,
        errors=errors,
    )
