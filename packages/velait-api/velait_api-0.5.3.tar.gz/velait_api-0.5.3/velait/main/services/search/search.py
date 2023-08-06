from django.conf import settings
from django.utils.translation import gettext_lazy as _

from velait.main.services.search.base_search import SearchOperator, Search, SearchError


class DjangoSearch(Search):
    DEFAULT_PAGE_SIZE = settings.REST_FRAMEWORK.get('PAGE_SIZE')

    def search(self):
        try:
            return self.model.objects.filter(**self.parse_query_filters()).order_by(*self._parse_ordering())
        except SearchError:
            raise SearchError(
                name="search",
                description=_("Поиск не может быть выполнен"),
            )

    def parse_query_filters(self):
        if self._query is None:
            return {}

        parsed_operators = (self._parse_operator(
            field_name=query_part.get('fn'),
            operator=query_part.get('op'),
            field_value=query_part.get('fv'),
        ) for query_part in self._query)

        return {field: field_filter for field, field_filter in parsed_operators}

    def _parse_operator(self, field_name: str, operator: str, field_value: str):
        """
        Creates an expression object if all input operators are valid.
        If they are not, raises op an exception
        """

        if operator == SearchOperator.LESS.value:
            return [f"{field_name}__lt", field_value]
        elif operator == SearchOperator.EQUAL.value:
            return [field_name, field_value]
        elif operator == SearchOperator.GREATER.value:
            return [f"{field_name}__gt", field_value]
        elif operator == SearchOperator.CONTAINS.value:
            return [f"{field_name}__in", field_value]
        elif operator == SearchOperator.LESS_OR_EQUAL.value:
            return [f"{field_name}__lte", field_value]
        elif operator == SearchOperator.GREATER_OR_EQUAL.value:
            return [f"{field_name}__gte", field_value]
        else:
            raise SearchError(name="query", description=_("Операция не найдена"))


__all__ = [
    'SearchOperator',
    'SearchError',
    'DjangoSearch',
]
