from django_filters import rest_framework as django_filter
from apiv1.tests.testing import *
from django.http import QueryDict

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.filters import BookFilter
from apiv1.tests.factories import BookFactory, BookFactoryWithThreeAuthors


class TestBookFilter(UserAPITestCase):
    """書籍検索フィルタのテストクラス"""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_filter_title(self):
        """タイトルによる絞り込み (正常系)"""

        # Arrange
        book_first = BookFactoryWithThreeAuthors(title='Test Book', created_by=self.user)
        book_second = BookFactoryWithThreeAuthors(title='テスト用の本', created_by=self.user)
        qd = QueryDict('title=test')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, book_first.id)

    def test_filter_authors(self):
        """著者名による絞り込み (正常系)"""

        # Arrange
        book_first = BookFactoryWithThreeAuthors(authors1__author__name='テスト次郎', created_by=self.user)
        book_second = BookFactoryWithThreeAuthors(created_by=self.user)
        qd = QueryDict('authors=次郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, book_first.id)

    # test_filter_status
    # test_filter_status_invalid_value
    # test_filter_accessed_at
    # test_filter_created_at
    # test_filter_q

    # test_and_search_inside_field
    # test_and_search_between_fields
    # test_or_search_inside_field
    # test_or_search_between_fields
