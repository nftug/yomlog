from django.core.exceptions import PermissionDenied
from rest_framework import status, viewsets, filters, pagination, response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from backend.models import *
from .serializers import BookOriginSerializer, BookCopySerializer


class GlobalViewMixin():
    def get_obj_for_user(self, pk, request, obj=BookOrigin):
        if request.user.is_superuser:
            return obj.objects.get(pk=pk)
        else:
            try:
                return obj.objects.get(pk=pk, created_by=request.user)
            except obj.DoesNotExist:
                raise PermissionDenied


class CustomPageNumberPagination(pagination.PageNumberPagination):
    """ページネーションクラス"""
    page_size = 12

    def get_paginated_response(self, data):
        return response.Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'totalPages': self.page.paginator.num_pages,
            'currentPage': self.page.number,
            'results': data
        })


class BookOriginViewSet(viewsets.ModelViewSet, GlobalViewMixin):
    """BookOriginのCRUD用APIクラス"""

    queryset = BookOrigin.objects.all()
    serializer_class = BookOriginSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author', 'books_copy__amazon_dp']

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.request.method != 'GET':
            return BookOrigin.objects.filter(created_by=self.request.user)
        else:
            return self.queryset


class BookCopyViewSet(viewsets.ModelViewSet, GlobalViewMixin):
    """BookCopyのCRUD用APIクラス"""

    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author', 'books_copy__amazon_dp']

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.request.method != 'GET':
            return BookCopy.objects.filter(created_by=self.request.user)
        else:
            return self.queryset
