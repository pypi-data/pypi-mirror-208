from rest_framework import pagination as _pagination

__all__ = [
    "PageSizePagination",
]


class PageSizePagination(_pagination.PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_page_size(self, request):
        if request.query_params.get(self.page_size_query_param, None) == "max":
            return self.max_page_size

        return super().get_page_size(request)
