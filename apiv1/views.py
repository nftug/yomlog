from rest_framework import serializers, status, viewsets, pagination, response, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as django_filter

from backend.models import Book, Note, StatusLog, Author
from .serializers import BookSerializer, NoteSerializer, StatusLogSerializer, AnalyticsSerializer
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
    # lookup_field = 'id_google'
    permission_classes = [IsAuthenticated]

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = BookFilter

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # プライベートアクセスのみ
        return self.queryset.filter(
            created_by=self.request.user
        ).prefetch_related('status_log', 'notes', 'authors').sort_by_state()

    def create(self, request, *args, **kwargs):
        # すでに同一のGoogle Books IDで登録されたレコードが存在する場合、保存せずにそのまま返す
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book = Book.objects.filter(created_by=request.user, id_google=serializer.validated_data['id_google'])

        if book.exists():
            serializer = BookSerializer(book.first())
            return response.Response(serializer.data, status.HTTP_200_OK)
        else:
            serializer.save()
            return response.Response(serializer.data, status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        # perform destroy
        instance = self.get_object()
        self.perform_destroy(instance)

        # orphanedなAuthorオブジェクトを削除
        queryset = Author.objects.filter(books=None)
        queryset.delete()

        return response.Response(status=status.HTTP_204_NO_CONTENT)


class StatusLogViewSet(viewsets.ModelViewSet):
    """StatusLogのCRUD用APIクラス"""

    queryset = StatusLog.objects.all()
    serializer_class = StatusLogSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = StatusLogFilter

    pagination_class = LogPagination

    def get_queryset(self):
        # ページネーションなしのオプションの場合
        if self.request.GET.get('no_pagination'):
            self.pagination_class = None

        # プライベートアクセスのみ
        return self.queryset.filter(created_by=self.request.user).select_related('book')


class NoteViewSet(viewsets.ModelViewSet):
    """NoteのCRUD用APIクラス"""

    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_class = [IsAuthenticated]
    parser_class = (FileUploadParser, FormParser)

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = NoteFilter

    pagination_class = LogPagination

    def get_queryset(self):
        # ページネーションなしのオプションの場合
        if self.request.GET.get('no_pagination'):
            self.pagination_class = None

        # プライベートアクセスのみ
        return self.queryset.filter(created_by=self.request.user).select_related('book')


class AnalyticsAPIView(views.APIView):
    """分析用のAPIクラス"""

    permission_class = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = StatusLog.objects.filter(created_by=request.user, position__gt=0).select_related('book')
        filterset = StatusLogFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            raise ValidationError(filterset.errors)

        serializer = AnalyticsSerializer(filterset.qs, context={'request': request})
        return response.Response(serializer.data, status.HTTP_200_OK)
