from rest_framework.response import Response


class APIResponse(Response):
    @staticmethod
    def format_data(data):
        return {
            "results": [data] if isinstance(data, dict) else data,
            "pagination": {
                'totalRecords': 1,
                'totalPages': 1,
                'first': None,
                'last': None,
                'next': None,
                'previous': None,
            },
            "errors": [],
        }

    def __init__(
        self,
        data=None,
        status=None,
        template_name=None,
        headers=None,
        exception=False,
        content_type=None,
        errors=None,
    ):
        if errors is not None:
            data = {
                "errors": [
                    {'name': error.name, 'description': error.description}
                    for error in errors
                ],
            }

        elif isinstance(data, dict):
            if data.get('pagination') is None:
                data = APIResponse.format_data(data)

        else:
            data = APIResponse.format_data(data)

        super(APIResponse, self).__init__(
            data=data,
            status=status,
            template_name=template_name,
            headers=headers,
            exception=exception,
            content_type=content_type,
        )
