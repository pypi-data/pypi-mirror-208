from typing import Optional

from rest_framework import pagination
from rest_framework.response import Response


class TranslateClientPagination(pagination.PageNumberPagination):
    """TranslateClient Pagination class."""

    page_size = 500
    page_size_query_param = "page_size"
    max_page_size = 800
    page_query_param = "page"

    def get_next_page(self) -> Optional[int]:
        if self.page.has_next():
            return self.page.next_page_number()
        return None

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "links": {"next": self.get_next_link(), "previous": self.get_previous_link()},
                "pages": {"current": self.page.number, "next": self.get_next_page()},
                "results": list(data),
            }
        )
