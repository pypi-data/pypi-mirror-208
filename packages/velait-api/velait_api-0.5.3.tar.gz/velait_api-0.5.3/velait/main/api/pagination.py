import json
from django.conf import settings
from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector
from rest_framework.utils.urls import replace_query_param, remove_query_param
from rest_framework.pagination import PageNumberPagination

from velait.main.api.responses import APIResponse


class VelaitPagination(PageNumberPagination):
    offset: int = None
    page_size: int = None

    def __parse_page_param(self, request):
        try:
            parsed_page = json.loads(request.query_params['page'])

            if not isinstance(parsed_page, dict):
                raise TypeError()

            if parsed_page.get('size') <= 0:
                parsed_page['size'] = settings.REST_FRAMEWORK,

            if parsed_page.get('offset', 0) <= 0:
                parsed_page['offset'] = 1

            self.page_size, self.offset = parsed_page['size'], parsed_page['offset']

        except (json.JSONDecodeError, TypeError, ValueError, KeyError):
            self.page_size, self.offset = settings.REST_FRAMEWORK['PAGE_SIZE'], 1

    def paginate_queryset(self, queryset, request, view=None):
        self.__parse_page_param(request)
        return super(VelaitPagination, self).paginate_queryset(queryset, request, view)

    def get_next_link(self):
        if not self.page.has_next():
            return None

        return replace_query_param(
            url=self.request.build_absolute_uri(),
            key=self.page_query_param,
            val=json.dumps({ "size": self.page_size, "offset": self.offset + 1 })
        )

    def get_previous_link(self):
        if not self.page.has_previous():
            return None

        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()

        if page_number == 1:
            return remove_query_param(url, self.page_query_param)

        return replace_query_param(
            url=url,
            key=self.page_query_param,
            val=json.dumps({ "size": self.page_size, "offset": self.offset - 1 })
        )

    def get_page_size(self, request):
        return self.page_size

    def get_page_number(self, request, paginator):
        return self.offset

    def get_paginated_response(self, data):
        return APIResponse({
            "pagination": {
                'totalRecords': self.page.paginator.count,
                'totalPages': self.page.paginator.num_pages,
                'first': remove_query_param(
                    url=self.request.build_absolute_uri(),
                    key=self.page_query_param,
                ),
                'last': replace_query_param(
                    url=self.request.build_absolute_uri(),
                    key=self.page_query_param,
                    val=json.dumps({
                        "size": self.page_size,
                        "offset": self.page.paginator.num_pages,
                    }),
                ),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            },
            "results": data,
            "errors": [],
        })


class VelaitPaginationInspector(PaginatorInspector):
    def get_paginated_response(self, paginator, response_schema):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "pagination": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'totalRecords': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'totalPages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'first': openapi.Schema(type=openapi.TYPE_STRING,
                                                format=openapi.FORMAT_URI, x_nullable=True),
                        'last': openapi.Schema(type=openapi.TYPE_STRING,
                                               format=openapi.FORMAT_URI, x_nullable=True),
                        'next': openapi.Schema(type=openapi.TYPE_STRING,
                                               format=openapi.FORMAT_URI, x_nullable=True),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING,
                                                   format=openapi.FORMAT_URI, x_nullable=True),
                    },
                ),
                'results': response_schema,
                'errors': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'description': openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            },
            required=['results'],
        )
