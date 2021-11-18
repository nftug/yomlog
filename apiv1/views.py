from django.core.exceptions import PermissionDenied
from rest_framework import status, viewsets, filters, pagination, response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters import rest_framework as django_filter

from backend.models import *
from .serializers import BookOriginSerializer, BookCopySerializer, StatusLogSerializer
from .filters import BookOriginFilter, BookCopyFilter, StatusLogFilter


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


class BookOriginViewSet(viewsets.ModelViewSet):
    """BookOriginのCRUD用APIクラス"""

    queryset = BookOrigin.objects.all()
    serializer_class = BookOriginSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = BookOriginFilter

    def get_queryset(self):
        if self.request.method != 'GET':
            # 編集や削除は作成したユーザーに限る
            return self.queryset.filter(created_by=self.request.user)
        else:
            # GETは全ユーザーで可能
            return self.queryset


class BookCopyViewSet(viewsets.ModelViewSet):
    """BookCopyのCRUD用APIクラス"""

    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = BookCopyFilter

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # プライベートアクセスのみ
        return self.queryset.filter(created_by=self.request.user)


class StatusLogViewSet(viewsets.ModelViewSet):
    """StatusLogのCRUD用APIクラス"""

    queryset = StatusLog.objects.all()
    serializer_class = StatusLogSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = StatusLogFilter

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        if self.request.method != 'GET':
            # 編集や削除は作成したユーザーに限る
            return self.queryset.filter(created_by=self.request.user)
        else:
            # GETは全ユーザーで可能
            return self.queryset
