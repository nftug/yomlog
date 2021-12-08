from rest_framework import status, viewsets, pagination, response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as django_filter

from backend.models import *
from .serializers import BookSerializer, NoteSerializer, StatusLogSerializer
from .filters import BookFilter, StatusLogFilter, NoteFilter
from rest_framework.parsers import FileUploadParser, FormParser


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


class LogPagination(CustomPageNumberPagination):
    """ページネーションクラス (ログ用)"""

    page_size = 24


class BookViewSet(viewsets.ModelViewSet):
    """BookのCRUD用APIクラス"""

    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = BookFilter

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # プライベートアクセスのみ
        return self.queryset.filter(created_by=self.request.user).sort_by_state()

    def create(self, request, *args, **kwargs):
        # すでに同一のGoogle Books IDで登録されたレコードが存在する場合、保存せずにそのまま返す
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book = self.queryset.filter(id_google=serializer.validated_data['id_google'])

        if book.exists():
            serializer = BookSerializer(book.first())
            return response.Response(serializer.data, status.HTTP_200_OK)
        else:
            serializer.save()
            return response.Response(serializer.data, status.HTTP_201_CREATED)


class StatusLogViewSet(viewsets.ModelViewSet):
    """StatusLogのCRUD用APIクラス"""

    queryset = StatusLog.objects.all().select_related('book')
    serializer_class = StatusLogSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = StatusLogFilter

    pagination_class = LogPagination

    def get_queryset(self):
        # プライベートアクセスのみ
        return self.queryset.filter(created_by=self.request.user)


class NoteViewSet(viewsets.ModelViewSet):
    """NoteのCRUD用APIクラス"""

    queryset = Note.objects.all().select_related('book')
    serializer_class = NoteSerializer
    permission_class = [IsAuthenticated]
    parser_class = (FileUploadParser, FormParser)

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = NoteFilter

    pagination_class = LogPagination

    def get_queryset(self):
        # プライベートアクセスのみ
        return self.queryset.filter(created_by=self.request.user)
