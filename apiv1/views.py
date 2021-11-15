from django.core.exceptions import PermissionDenied
from rest_framework import status, viewsets, filters, pagination, response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from backend.models import Book
from .serializers import BookSerializer


class GlobalViewMixin():
    def get_obj_for_user(self, pk, request, obj=Book):
        if request.user.is_superuser:
            return obj.objects.get(pk=pk)
        else:
            try:
                return obj.objects.get(pk=pk, created_by=request.user)
            except obj.DoesNotExist:
                raise PermissionDenied


class CustomPageNumberPagination(pagination.PageNumberPagination):
    """ページネーションクラス"""
    page_size = 3

    def get_paginated_response(self, data):
        return response.Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'totalPages': self.page.paginator.num_pages,
            'currentPage': self.page.number,
            'results': data
        })


class BookViewSet(viewsets.ModelViewSet, GlobalViewMixin):
    """本モデルのCRUD用APIクラス"""

    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    pagination_class = CustomPageNumberPagination

    def update(self, request, *args, **kwargs):
        instance = self.get_obj_for_user(pk=self.kwargs['pk'], request=request)
        serializer = BookSerializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_obj_for_user(pk=self.kwargs['pk'], request=request)
        instance.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
