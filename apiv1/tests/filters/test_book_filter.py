from django_filters import rest_framework as django_filter
from apiv1.tests.mixins import *
from django.http import QueryDict

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.filters import BookFilter


class TestBookFilter(UserAPITestCase):
    """書籍検索フィルタのテストクラス"""

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_filter_title(self):
        """タイトルによる絞り込み (正常系)"""

        book_first_fixture = get_book_fixture(
            title='Test Book',
            authors=['テスト太郎', 'Jane Doe'],
            amazon_dp='1234567890123'
        )
        book_second_fixture = get_book_fixture(
            title='テスト用の本',
            authors=['テスト太郎', 'Jane Doe'],
            amazon_dp='0234567890123'
        )
        book_first = create_dummy_book(book_first_fixture, self.user)
        book_second = create_dummy_book(book_second_fixture, self.user)
        qd = QueryDict('title=test')
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, book_first.id)

    # test_filter_authors
    # test_filter_status
    # test_filter_status_invalid_value
    # test_filter_accessed_at
    # test_filter_created_at
    # test_filter_q

    # test_and_search_inside_field
    # test_and_search_between_fields
    # test_or_search_inside_field
    # test_or_search_between_fields
