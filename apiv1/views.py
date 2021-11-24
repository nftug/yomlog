from django.core.exceptions import PermissionDenied, ValidationError
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

    def create(self, request, *args, **kwargs):
        # すでにタイトルと著者名が一致する本が存在する場合、保存せずにそのまま返す

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        author = serializer.data['author']
        book_origin = BookOrigin.objects.filter(title=title, author=author)

        if book_origin.exists():
            serializer = BookOriginSerializer(book_origin.first())
            return response.Response(serializer.data, status.HTTP_200_OK)
        else:
            serializer.save()
            return response.Response(serializer.data, status.HTTP_201_CREATED)


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

    def create(self, request, *args, **kwargs):
        # すでにBookOriginをもとにしたレコードが存在する場合、保存せずにそのまま返す

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book_origin_id = serializer.data['book_origin']
        book_origin = BookOrigin.objects.filter(created_by=request.user, book_origin=book_origin_id)

        if book_origin.exists():
            serializer = BookOriginSerializer(book_origin.first())
            return response.Response(serializer.data, status.HTTP_200_OK)
        else:
            serializer.save()
            return response.Response(serializer.data, status.HTTP_201_CREATED)


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
