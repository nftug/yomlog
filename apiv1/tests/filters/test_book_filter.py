from datetime import datetime
from django.http import QueryDict
from django.utils.timezone import make_aware
from datetime import datetime

from backend.models import Book
from apiv1.tests.testing import *
from apiv1.filters import BookFilter
from apiv1.tests.factories import BookFactory, BookFactoryWithThreeAuthors, StatusLogFactory


class TestBookFilter(UserAPITestCase):
    """書籍検索フィルタのテストクラス"""

    def test_filter_title(self):
        """タイトルによる絞り込み (正常系)"""

        # Arrange
        book_first = BookFactory(title='Test Book', created_by=self.user)
        book_second = BookFactory(title='テスト用の本', created_by=self.user)
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
        book_first = BookFactoryWithThreeAuthors(
            authors1__author__name='テスト次郎',
            authors2__author__name='Test Taro',
            authors3__author__name='Jane Doe',
            created_by=self.user
        )
        book_second = BookFactoryWithThreeAuthors(
            authors1__author__name='テスト太郎',
            authors2__author__name='Test Taro',
            authors3__author__name='Jane Doe',
            created_by=self.user
        )
        qd = QueryDict('authors=次郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, book_first.id)

    def test_filter_state_reading(self):
        """ステータスによる絞り込み (正常系: reading)"""

        # Arrange
        book_first = BookFactory(created_by=self.user)
        book_second = BookFactory(created_by=self.user)
        book_third = BookFactory(created_by=self.user)

        StatusLogFactory(position=1, book=book_first, created_by=self.user)
        StatusLogFactory(position=1, book=book_second, created_by=self.user)
        StatusLogFactory(position=book_second.total, book=book_second, created_by=self.user)

        qd = QueryDict('state=reading')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, book_first.id)

    def test_filter_state_read(self):
        """ステータスによる絞り込み (正常系: read)"""

        # Arrange
        book_first = BookFactory(created_by=self.user)
        book_second = BookFactory(created_by=self.user)
        book_third = BookFactory(created_by=self.user)

        StatusLogFactory(position=1, book=book_first, created_by=self.user)
        StatusLogFactory(position=book_first.total, book=book_first, created_by=self.user)
        StatusLogFactory(position=1, book=book_second, created_by=self.user)

        qd = QueryDict('state=read')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, book_first.id)

    def test_filter_state_to_be_read(self):
        """ステータスによる絞り込み (正常系: to_be_read)"""

        # Arrange
        book_first = BookFactory(created_by=self.user)
        book_second = BookFactory(created_by=self.user)
        book_third = BookFactory(created_by=self.user)

        StatusLogFactory(position=1, book=book_first, created_by=self.user)
        StatusLogFactory(position=0, book=book_first, created_by=self.user)
        StatusLogFactory(position=1, book=book_second, created_by=self.user)

        qd = QueryDict('state=to_be_read')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.first().id, book_first.id)

    def test_filter_state_all(self):
        """ステータスによる絞り込み (正常系: all)"""

        # Arrange
        book_first = BookFactory(created_by=self.user)
        book_second = BookFactory(created_by=self.user)
        book_third = BookFactory(created_by=self.user)

        StatusLogFactory(position=1, book=book_first, created_by=self.user)
        StatusLogFactory(position=book_second.total, book=book_second, created_by=self.user)

        qd = QueryDict('state=all')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 3)

    def test_filter_state_not_reading(self):
        """ステータスによる絞り込み (正常系: not reading)"""

        # Arrange
        book_first = BookFactory(created_by=self.user)
        book_second = BookFactory(created_by=self.user)
        book_third = BookFactory(created_by=self.user)

        StatusLogFactory(position=1, book=book_first, created_by=self.user)
        StatusLogFactory(position=1, book=book_second, created_by=self.user)
        StatusLogFactory(position=book_second.total, book=book_second, created_by=self.user)

        qd = QueryDict('state_not=reading')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(id=book_second.id).exists(), True)
        self.assertEqual(queryset.filter(id=book_third.id).exists(), True)

    def test_filter_state_invalid_value(self):
        """ステータスによる絞り込み (異常系: 不正な値)"""

        # Arrange
        book_first = BookFactory(created_by=self.user)
        qd = QueryDict('state=hoge')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())

        # Assert
        self.assertNotEqual(filterset.is_valid, True)

    def test_filter_created_at(self):
        """ステータスによる絞り込み (正常系: 作成日の範囲)"""

        # Arrange
        book_first = BookFactory(created_at=make_aware(datetime(2022, 1, 1)), created_by=self.user)
        book_second = BookFactory(created_at=make_aware(datetime(2022, 1, 3)), created_by=self.user)
        qd = QueryDict('created_at_after=2022-01-01&created_at_before=2022-01-02')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, book_first.id)

    def test_filter_accessed_at(self):
        """ステータスによる絞り込み (正常系: アクセス日の範囲)"""

        # Arrange
        book_first = BookFactory(created_at=make_aware(datetime(2022, 1, 1)), created_by=self.user)
        book_second = BookFactory(created_at=make_aware(datetime(2022, 1, 3)), created_by=self.user)
        book_third = BookFactory(created_at=make_aware(datetime(2022, 1, 5)), created_by=self.user)
        state = StatusLogFactory(book=book_first, created_at=make_aware(datetime(2022, 1, 6)), created_by=self.user)
        qd = QueryDict('accessed_at_after=2022-01-05&accessed_at_before=2022-01-06')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)
        self.assertEqual(queryset.filter(id=book_third.id).exists(), True)

    def test_filter_q(self):
        """フリーワードによる絞り込み (正常系)"""

        # Arrange
        book_first = BookFactory(title='あいうえお', authors__author__name='テスト太郎', created_by=self.user)
        book_second = BookFactoryWithThreeAuthors(
            title='かきくけこ',
            authors1__author__name='テスト太郎',
            authors2__author__name='Test Taro',
            authors3__author__name='あいうえお',
            created_by=self.user
        )
        book_third = BookFactory(title='さしすせそ', authors__author__name='テスト太郎', created_by=self.user)
        qd = QueryDict('q=あいうえお')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)
        self.assertEqual(queryset.filter(id=book_second.id).exists(), True)

    def test_and_search_inside_field(self):
        """AND検索 (フィールド内)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        book_second = BookFactory(title='ほげほげ2', authors__author__name='テスト二郎', created_by=self.user)
        book_third = BookFactory(title='ほげほげ3', authors__author__name='テスト三郎', created_by=self.user)
        qd = QueryDict('q=ほげほげ　一郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)

    def test_and_search_between_fields(self):
        """AND検索 (フィールド間)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        book_second = BookFactory(title='ほげほげ2', authors__author__name='テスト二郎', created_by=self.user)
        book_third = BookFactory(title='ほげほげ3', authors__author__name='テスト三郎', created_by=self.user)
        qd = QueryDict('title=ほげほげ&authors=一郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)

    def test_or_search_inside_field(self):
        """OR検索 (フィールド内)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        book_second = BookFactory(title='ほげほげ2', authors__author__name='テスト二郎', created_by=self.user)
        book_third = BookFactory(title='ほげほげ3', authors__author__name='テスト三郎', created_by=self.user)
        qd = QueryDict('q=ほげほげ1 OR 二郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)
        self.assertEqual(queryset.filter(id=book_second.id).exists(), True)

    def test_or_search_between_fields(self):
        """OR検索 (フィールド間)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        book_second = BookFactory(title='ほげほげ2', authors__author__name='テスト二郎', created_by=self.user)
        book_third = BookFactory(title='ほげほげ3', authors__author__name='テスト三郎', created_by=self.user)
        qd = QueryDict('title=ほげほげ1&authors_or=二郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)
        self.assertEqual(queryset.filter(id=book_second.id).exists(), True)

    def test_or_and_search_inside_field(self):
        """AND/OR検索の併用 (フィールド内)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        book_second = BookFactory(title='ほげほげ2', authors__author__name='テスト二郎', created_by=self.user)
        book_third = BookFactory(title='ほげほげ3', authors__author__name='テスト三郎', created_by=self.user)
        qd = QueryDict('q=ほげほげ 一郎 OR 二郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)
        self.assertEqual(queryset.filter(id=book_second.id).exists(), True)

    def test_or_and_search_between_fields(self):
        """AND/OR検索の併用 (フィールド間)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        book_second = BookFactory(title='ほげほげ2', authors__author__name='テスト二郎', created_by=self.user)
        book_third = BookFactory(title='ほげほげ3', authors__author__name='テスト三郎', created_by=self.user)
        qd = QueryDict('title=ほげほげ&authors=一郎&authors_or=二郎')

        # Act
        filterset = BookFilter(qd, queryset=Book.objects.all())
        queryset = filterset.qs.sort_by_accessed_at()

        # Assert
        self.assertEqual(queryset.count(), 2)
        self.assertEqual(queryset.filter(id=book_first.id).exists(), True)
        self.assertEqual(queryset.filter(id=book_second.id).exists(), True)
