import re
from typing import Type, List
from uuid import UUID

from drf_yasg import openapi
from django.conf import settings
from django.db.models import Q, QuerySet
from rest_framework.request import Request
from drf_yasg.utils import swagger_auto_schema
from django.utils.translation import gettext_lazy as _
from rest_framework.serializers import ModelSerializer
from rest_framework.generics import GenericAPIView, ListAPIView

from velait.main.models import BaseModel
from velait.main.exceptions import VelaitError
from velait.main.api.responses import APIResponse
from velait.main.api.serializers import BaseSerializer
from velait.main.services.search.search import SearchError, DjangoSearch
from velait.main.api.pagination import VelaitPagination, VelaitPaginationInspector


class SearchView(GenericAPIView):
    model: Type[BaseModel] = None
    serializer_class: Type[ModelSerializer] = None
    search_class: Type[DjangoSearch] = DjangoSearch
    pagination_class = VelaitPagination

    def __init__(self, *args, **kwargs):
        super(SearchView, self).__init__(*args, **kwargs)

        if self.model is None or self.serializer_class is None:
            raise NotImplementedError("Model or Serializer were not supplied to the SearchView")

    def get_search_object(self):
        return self.search_class(
            query=self.request.GET.get('query'),
            ordering=self.request.GET.get('ordering'),
            model=self.model,
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="search",
                in_=openapi.IN_QUERY,
                type='string',
                description='Search string',
            ),
            openapi.Parameter(
                name="query",
                in_=openapi.IN_QUERY,
                type='[{ fn: string, op: string, fv: any }]',
                description='Query parameter for search',
            ),
            openapi.Parameter(
                name="ordering",
                in_=openapi.IN_QUERY,
                type='string',
                description='Ordering fields separated by commas. Use - in front of the field to order by desc',
            ),
            openapi.Parameter(
                name="page",
                in_=openapi.IN_QUERY,
                type='{ offset: int, page: int }',
                description='Page parameter for pagination.',
            ),
        ],
        pagination_class=VelaitPagination,
        paginator_inspectors=[VelaitPaginationInspector],
    )
    def get(self, request, *args, **kwargs):
        try:
            search = self.get_search_object()
            paginator = self.pagination_class()
            queryset = paginator.paginate_queryset(queryset=search.search(), request=request, view=self)
            return paginator.get_paginated_response(self.serializer_class(instance=queryset, many=True).data)
        except SearchError as exc:
            return APIResponse(errors=[exc], status=400)


class ModelRefsView(ListAPIView):
    serializer_class: Type[BaseSerializer]
    queryset: QuerySet
    uuid_field_name: str = 'id'
    numerical_field_name: str = "pk"
    pagination_class = VelaitPagination

    def _apply_queryset_filters(self, numerical_ids: List[int], uuids: List[UUID]) -> QuerySet:
        return self.queryset.filter(
            Q(**{f"{self.numerical_field_name}__in": numerical_ids})
            | Q(**{f"{self.uuid_field_name}__in": uuids}),
        )[:getattr(settings, "ID_LISTING_MAX_RESULTS", 200)]

    def get_queryset(self):
        searched_ids = self.request.query_params.get('ids')

        if searched_ids is None:
            return APIResponse(errors={
                VelaitError(
                    name="query",
                    description=_("You must provide 'ids' query parameter to use this view"),
                ),
            })

        numerical_ids, uuids = [], []

        for id_ in searched_ids.split(","):
            if re.fullmatch(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", id_):
                uuids.append(id_)
            elif re.fullmatch(r'\d+', id_):
                numerical_ids.append(int(id_))
            else:
                return APIResponse(errors={
                    VelaitError(
                        name="query",
                        description=_("Id must be numbers or UUID. Your format is invalid"),
                    ),
                })

        return self._apply_queryset_filters(numerical_ids=numerical_ids, uuids=uuids)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="ids",
                in_=openapi.IN_QUERY,
                type='list',
                description="Ids of the models you need to query",
            ),
        ],
        pagination_class=VelaitPagination,
        paginator_inspectors=[VelaitPaginationInspector],
    )
    def get(self, request: Request, *args, **kwargs):
        return APIResponse(
            data=self.serializer_class(instance=self.get_queryset(), many=True).data,
            status=200,
        )


__all__ = [
    'ModelRefsView',
    'SearchView',
]
