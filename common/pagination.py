from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination


class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'  # Optional: let client override
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'page': self.page.number,
            'pages': self.page.paginator.num_pages,
            'results': data
        })

class AppUserCursorPagination(CursorPagination):
    page_size = 100
    ordering = '-created' 
    cursor_query_param = 'cursor'