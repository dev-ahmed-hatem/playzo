from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    page_size = 10

    def paginate_queryset(self, queryset, request, view=None):
        no_pagination = request.query_params.get("no_pagination", None)
        if no_pagination and no_pagination.lower() == 'true':
            return None
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'total_pages': total_pages,
            'page': self.page.number,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'data': data,
        })
