from rest_framework import status, viewsets, pagination, response, views, generics
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as django_filter

from backend.models import Book, Note, StatusLog, Author
from .serializers import AuthorSerializer, BookSerializer, NoteSerializer, StatusLogSerializer, AnalyticsSerializer
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

    queryset = Book.objects.none()
    serializer_class = BookSerializer
    # lookup_field = 'id_google'

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = BookFilter

    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        # プライベートアクセスのみ
        return Book.objects.filter(
            created_by=self.request.user
        ).prefetch_related('status_log', 'notes', 'authors').sort_by_accessed_at()

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
        Author.objects.filter(books=None).delete()

        return response.Response(status=status.HTTP_204_NO_CONTENT)


class StatusLogViewSet(viewsets.ModelViewSet):
    """StatusLogのCRUD用APIクラス"""

    queryset = StatusLog.objects.none()
    serializer_class = StatusLogSerializer

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = StatusLogFilter

    pagination_class = LogPagination

    def get_queryset(self):
        # ページネーションなしのオプションの場合
        if self.request.GET.get('no_pagination'):
            self.pagination_class = None

        # プライベートアクセスのみ
        return StatusLog.objects.filter(created_by=self.request.user).select_related('book')


class NoteViewSet(viewsets.ModelViewSet):
    """NoteのCRUD用APIクラス"""

    queryset = Note.objects.none()
    serializer_class = NoteSerializer
    parser_class = (FileUploadParser, FormParser)

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = NoteFilter

    pagination_class = LogPagination

    def get_queryset(self):
        # ページネーションなしのオプションの場合
        if self.request.GET.get('no_pagination'):
            self.pagination_class = None

        # プライベートアクセスのみ
        return Note.objects.filter(created_by=self.request.user).select_related('book')


class AnalyticsAPIView(views.APIView):
    """分析用のAPIクラス"""

    def get(self, request, *args, **kwargs):
        queryset = StatusLog.objects.filter(created_by=request.user, position__gt=0).select_related('book')
        filterset = StatusLogFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            raise ValidationError(filterset.errors)

        serializer = AnalyticsSerializer(filterset.qs, context={'request': request})
        return response.Response(serializer.data, status.HTTP_200_OK)


class AuthorListAPIView(generics.ListAPIView):
    """著者名リストのAPI"""

    queryset = Book.objects.none()
    serializer_class = AuthorSerializer

    filter_backends = [django_filter.DjangoFilterBackend]
    filterset_class = BookFilter

    pagination_class = LogPagination

    def list(self, request, *args, **kwargs):
        # Booksをフィルタリングして、条件に合致するAuthorのquerysetを取得
        books = self.filter_queryset(Book.objects.filter(created_by=request.user))
        queryset = Author.objects.filter(books__in=books).sort_by_books_count()

        if not self.request.GET.get('no_pagination'):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response(serializer.data)
