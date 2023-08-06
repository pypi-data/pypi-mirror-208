import json
import re
from enum import Enum
from abc import abstractmethod, ABC
from typing import Optional

from velait.main.exceptions import VelaitError


class SearchError(VelaitError):
    status_code = 400

    def __init__(self, name: str, description: str):
        super(SearchError, self).__init__(description)
        self.description = description
        self.name = name


class PaginationLimitsError(VelaitError):
    description = "page"
    name = "Pagination limits are invalid"
    status_code = 400


class SearchOperator(Enum):
    LESS = "less"
    EQUAL = "equal"
    GREATER = "greater"
    CONTAINS = "contains"
    LESS_OR_EQUAL = "lessOrEqual"
    GREATER_OR_EQUAL = "greaterOrEqual"


class Search(ABC):
    def _parse_json(self, data, key_name: str):
        try:
            return json.loads(data)
        except (json.JSONDecodeError, TypeError, ValueError):
            if data is not None:
                raise SearchError(
                    name=key_name,
                    description=f"'{key_name}' cannot be parsed as JSON",
                )

    def __init__(self, query: str, ordering: Optional[str], model):
        self.model = model
        self._query = self._parse_json(data=query, key_name='query') or []
        self._ordering = tuple(map(str.strip, ordering.split(","))) if ordering else ()
        self.validate()

    def _validate_query_part(self, query_part: dict):
        name = query_part.get('fn')
        operation = query_part.get('op')

        if (name is None) or (operation is None):
            raise SearchError(
                name='query',
                description="All items in 'query' must have 'fn', 'op', 'fv' keys",
            )
        elif name not in self.model.queryable_fields:
            raise SearchError(
                name="query",
                description=f"{name} was not found as a value",
            )

    def _format_query_part(self, query_part: dict) -> dict:
        return {
            **query_part,
            "fn": re.sub(r'(?<!^)(?=[A-Z])', '_', query_part["fn"]).lower(),
        }

    def validate(self):
        if isinstance(self._query, list):
            for i in range(len(self._query)):
                self._query[i] = self._format_query_part(self._query[i])
                self._validate_query_part(self._query[i])

        elif self._query is not None:
            raise SearchError(
                name="query",
                description=f"Field 'query' must be a list of filters",
            )

        ordering = []

        for field in self._ordering:
            if field.startswith('-'):
                ordering.append(field[1:])
            else:
                ordering.append(field)

        not_orderable_fields = set(ordering) - set(self.model.orderable_fields)

        if self._ordering and not_orderable_fields:
            parsed_fields = ' ,'.join(f"'{field}'" for field in not_orderable_fields)
            raise SearchError(
                name="ordering",
                description=f"Fields {parsed_fields} cannot be used in 'ordering'",
            )

    @abstractmethod
    def _parse_operator(self, field_name: str, operator: str, field_value: str):
        raise NotImplementedError("_parse_operator() is not implemented")

    def _parse_ordering(self):
        return self._ordering

    @abstractmethod
    def search(self):
        raise NotImplementedError("search() is not implemented")

    def parse_query_filters(self):
        return [self._parse_operator(
            field_name=query_part.get('fn'),
            operator=query_part.get('op'),
            field_value=query_part.get('fv'),
        ) for query_part in self._query]


__all__ = [
    'Search',
    'SearchError',
    'SearchOperator'
]
