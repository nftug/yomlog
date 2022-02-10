import freezegun
from django.http import QueryDict
from django.utils.timezone import now, make_aware, datetime, timedelta
from collections import OrderedDict
from django.test import RequestFactory

from apiv1.tests.testing import *
from apiv1.tests.factories import BookFactory, BookFactoryWithThreeAuthors, CustomUserFactory, StatusLogFactory
from apiv1.serializers import AnalyticsSerializer, AuthorSerializer, PagesDailySerializer
from apiv1.filters import StatusLogFilter
from backend.models import Author, BookAuthorRelation


def create_status_fixture_for_pages_read(user):
    book_first = BookFactory(created_by=user, total=100)
    book_second = BookFactory(created_by=user, total=210)

    StatusLogFactory(
        created_by=user, book=book_first, position=21, created_at=make_aware(datetime(2022, 1, 1, 0, 0))
    )
    StatusLogFactory(
        created_by=user, book=book_first, position=12, created_at=make_aware(datetime(2022, 1, 1, 0, 1))
    )
    StatusLogFactory(
        created_by=user, book=book_second, position=12, created_at=make_aware(datetime(2022, 1, 2, 0, 0))
    )
    StatusLogFactory(
        created_by=user, book=book_second, position=0, created_at=make_aware(datetime(2022, 1, 2, 0, 1))
    )
    StatusLogFactory(
        created_by=user, book=book_second, position=5, created_at=make_aware(datetime(2022, 1, 2, 0, 2))
    )
    StatusLogFactory(
        created_by=user, book=book_second, position=27, created_at=make_aware(datetime(2022, 1, 2, 0, 3))
    )
    StatusLogFactory(
        created_by=user, book=book_second, position=30, created_at=make_aware(datetime(2022, 1, 3, 0, 0))
    )
    StatusLogFactory(
        created_by=user, book=book_first, position=51, created_at=make_aware(datetime(2022, 1, 3, 0, 1))
    )


def create_status_fixture_for_days(user):
    start_at = make_aware(datetime(2022, 1, 1))

    for i in range(4):
        StatusLogFactory(created_by=user, created_at=start_at + timedelta(days=i))

    start_at += timedelta(days=i + 2)

    for i in range(2):
        StatusLogFactory(created_by=user, created_at=start_at + timedelta(days=i))
        StatusLogFactory(created_by=user, created_at=start_at + timedelta(days=i))


class TestAnalyticsSerializer(UserSerializerTestCase):
    """AnalyticsSerializerのテストクラス"""

    def setUp(self):
        super().setUp()
        self.request = RequestFactory().get('/')
        self.user = CustomUserFactory(date_joined=make_aware(datetime(2022, 1, 1)))
        self.request.user = self.user
        self.context = {'request': self.request}

    def test_get_number_of_books(self):
        """冊数集計の取得 (正常系)"""

        # Arrange
        book_no_state = BookFactory(created_by=self.user, total=100)
        book_to_be_read = BookFactory(created_by=self.user, total=100)
        book_reading = BookFactory(created_by=self.user, total=100)
        book_read = BookFactory(created_by=self.user, total=100)

        StatusLogFactory(
            created_by=self.user, book=book_to_be_read, position=10, created_at=now()
        )
        StatusLogFactory(
            created_by=self.user, book=book_to_be_read, position=0, created_at=now() + timedelta(seconds=1)
        )
        StatusLogFactory(created_by=self.user, book=book_reading, position=50)
        StatusLogFactory(created_by=self.user, book=book_read, position=100)

        # Act
        data = AnalyticsSerializer(StatusLog.objects.all(), context=self.context).data

        # Assert
        result = data['number_of_books']
        self.assertEqual(result['to_be_read'], 2)
        self.assertEqual(result['reading'], 1)
        self.assertEqual(result['read'], 1)
        self.assertEqual(result['all'], 4)

    def test_get_number_of_books_filtered(self):
        """冊数集計の取得 (正常系: 日付範囲指定)"""

        # Arrange
        book_no_state = BookFactory(created_by=self.user, total=100)
        book_reading = BookFactory(created_by=self.user, total=100)
        book_read = BookFactory(created_by=self.user, total=100)

        StatusLogFactory(
            created_by=self.user, book=book_reading, position=50, created_at=make_aware(datetime(2022, 1, 1))
        )
        StatusLogFactory(
            created_by=self.user, book=book_read, position=100, created_at=make_aware(datetime(2022, 1, 5))
        )

        # Act
        queryset = StatusLog.objects.filter(
            created_at__gte=make_aware(datetime(2022, 1, 1)), created_at__lte=make_aware(datetime(2022, 1, 2))
        )
        data = AnalyticsSerializer(queryset, context=self.context).data

        # Assert
        result = data['number_of_books']
        self.assertEqual(result['reading'], 1)
        self.assertEqual(result['read'], 0)
        # self.assertEqual(result['to_be_read'], 2)
        # self.assertEqual(result['all'], 3)

    @freezegun.freeze_time('2022-01-04')
    def test_get_pages_read(self):
        """ページ数集計の取得 (正常系)"""

        # Arrange
        create_status_fixture_for_pages_read(user=self.user)

        # Act
        data = AnalyticsSerializer(StatusLog.objects.all(), context=self.context).data

        # Assert
        result = data['pages_read']
        self.assertEqual(result['total'], 97)
        self.assertEqual(result['avg_per_day'], 24)

    @freezegun.freeze_time('2022-01-04')
    def test_get_pages_read_threshold(self):
        """ページ数集計の取得 (正常系: thresholdあり)"""

        # Arrange
        self.user.date_joined = make_aware(datetime(2022, 1, 2))
        create_status_fixture_for_pages_read(user=self.user)

        # Act
        data = AnalyticsSerializer(StatusLog.objects.all(), context=self.context).data

        # Assert
        result = data['pages_read']
        self.assertEqual(result['total'], 97)
        self.assertEqual(result['avg_per_day'], 25)

    def test_get_pages_read_filtered(self):
        """ページ数集計の取得 (正常系: 日付範囲フィルタ)"""

        # Arrange
        create_status_fixture_for_pages_read(user=self.user)

        qd = QueryDict('created_at_after=2022-01-02&created_at_before=2022-01-02')
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs
        context = {**self.context, 'filterset': filterset}

        # Act
        data = AnalyticsSerializer(queryset, context=context).data

        # Assert
        result = data['pages_read']
        self.assertEqual(result['total'], 34)
        self.assertEqual(result['avg_per_day'], 34)

    def test_get_pages_read_filtered_blank_after(self):
        """ページ数集計の取得 (正常系: 日付範囲フィルタ 開始日が空欄)"""

        # Arrange
        create_status_fixture_for_pages_read(user=self.user)

        qd = QueryDict('created_at_before=2022-01-02')
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs
        context = {**self.context, 'filterset': filterset}

        # Act
        data = AnalyticsSerializer(queryset, context=context).data

        # Assert
        result = data['pages_read']
        self.assertEqual(result['total'], 55)
        self.assertEqual(result['avg_per_day'], 27)

    @freezegun.freeze_time('2022-01-04')
    def test_get_pages_read_filtered_blank_before(self):
        """ページ数集計の取得 (正常系: 日付範囲フィルタ 終了日が空欄)"""

        # Arrange
        create_status_fixture_for_pages_read(user=self.user)

        qd = QueryDict('created_at_after=2022-01-02')
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs
        context = {**self.context, 'filterset': filterset}

        # Act
        data = AnalyticsSerializer(queryset, context=context).data

        # Assert
        result = data['pages_read']
        self.assertEqual(result['total'], 76)
        self.assertEqual(result['avg_per_day'], 25)

    @freezegun.freeze_time('2022-01-04')
    def test_get_pages_read_filtered_threshold(self):
        """ページ数集計の取得 (正常系: 日付範囲フィルタ thresholdあり)"""

        # Arrange
        self.user.date_joined = make_aware(datetime(2022, 1, 2))
        create_status_fixture_for_pages_read(user=self.user)

        qd = QueryDict()
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs
        context = {**self.context, 'filterset': filterset}

        # Act
        data = AnalyticsSerializer(queryset, context=context).data

        # Assert
        result = data['pages_read']
        self.assertEqual(result['total'], 97)
        self.assertEqual(result['avg_per_day'], 25)

    @freezegun.freeze_time('2022-01-08')
    def test_get_days(self):
        """日数集計の取得 (正常系)"""

        # Arrange
        self.user.date_joined = make_aware(datetime(2022, 1, 1))
        create_status_fixture_for_days(user=self.user)

        # Act
        data = AnalyticsSerializer(StatusLog.objects.all(), context=self.context).data

        # Assert
        result = data['days']
        self.assertEqual(result['total'], 6)
        self.assertEqual(result['continuous'], 2)
        self.assertEqual(result['continuous_max'], 4)

    @freezegun.freeze_time('2022-01-08')
    def test_get_days_with_no_status(self):
        """日数集計の取得 (正常系: ステータスなし)"""

        # Arrange
        self.user.date_joined = make_aware(datetime(2022, 1, 1))

        # Act
        data = AnalyticsSerializer(StatusLog.objects.all(), context=self.context).data

        # Assert
        result = data['days']
        self.assertEqual(result['total'], 0)
        self.assertEqual(result['continuous'], 0)
        self.assertEqual(result['continuous_max'], 0)

    def test_get_days_filtered(self):
        """日数集計の取得 (正常系: 日付範囲フィルタ)"""

        # Arrange
        create_status_fixture_for_days(user=self.user)

        qd = QueryDict('created_at_after=2022-01-02&created_at_before=2022-01-06')
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs
        context = {**self.context, 'filterset': filterset}

        # Act
        data = AnalyticsSerializer(queryset, context=context).data

        # Assert
        result = data['days']
        self.assertEqual(result['total'], 4)
        self.assertEqual(result['continuous'], 1)
        self.assertEqual(result['continuous_max'], 3)

    def test_get_days_filtered_blank_after(self):
        """日数集計の取得 (正常系: 日付範囲フィルタ 開始日が空欄)"""

        # Arrange
        self.user.date_joined = make_aware(datetime(2022, 1, 2))
        create_status_fixture_for_days(user=self.user)

        qd = QueryDict('created_at_before=2022-01-06')
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs
        context = {**self.context, 'filterset': filterset}

        # Act
        data = AnalyticsSerializer(queryset, context=context).data

        # Assert
        result = data['days']
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['continuous'], 1)
        self.assertEqual(result['continuous_max'], 4)

    @freezegun.freeze_time('2022-01-08')
    def test_get_days_filtered_blank_before(self):
        """日数集計の取得 (正常系: 日付範囲フィルタ 終了日が空欄)"""

        # Arrange
        self.user.date_joined = make_aware(datetime(2022, 1, 2))
        create_status_fixture_for_days(user=self.user)

        qd = QueryDict('created_at_after=2022-01-02')
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs
        context = {**self.context, 'filterset': filterset}

        # Act
        data = AnalyticsSerializer(queryset, context=context).data

        # Assert
        result = data['days']
        self.assertEqual(result['total'], 5)
        self.assertEqual(result['continuous'], 2)
        self.assertEqual(result['continuous_max'], 3)


class TestPagesDailySerializer(UserAPITestCase):
    """PagesDailySerializerのテストクラス"""

    def setUp(self):
        super().setUp()
        self.request = RequestFactory().get('/')
        self.user = CustomUserFactory(date_joined=make_aware(datetime(2022, 1, 1)))
        self.request.user = self.user
        self.context = {'request': self.request}

    def test_get_pages_daily(self):
        """一日ごとのページ数を取得 (正常系)"""

        # Arranage
        create_status_fixture_for_pages_read(user=self.user)
        queryset = StatusLog.objects.all()
        date_set = set(queryset.values_list('created_at__date', flat=True))
        date_list = sorted(list(date_set), reverse=True)

        # Act
        data = PagesDailySerializer(date_list, context={**self.context, 'queryset': queryset}, many=True).data

        # Assert
        self.assertEqual(len(data), 3)
        expected_results = [
            {'date': datetime(2022, 1, 3).date(), 'pages': 42},
            {'date': datetime(2022, 1, 2).date(), 'pages': 34},
            {'date': datetime(2022, 1, 1).date(), 'pages': 21}
        ]
        for i in range(3):
            self.assertEqual(dict(data[i], expected_results[i]))


class TestAuthorSerializer(UserAPITestCase):
    """AuthorSerializerのテストクラス"""

    def setUp(self):
        super().setUp()
        self.request = RequestFactory().get('/')
        self.user = CustomUserFactory(date_joined=make_aware(datetime(2022, 1, 1)))
        self.request.user = self.user
        self.context = {'request': self.request}

    def test_get_authors(self):
        """著者リストを取得 (正常系)"""

        # Arrange
        book1 = BookFactory(authors__author__name='Test', title='テスト1')
        book2 = BookFactory(authors=None, title='テスト2')
        BookAuthorRelation.objects.create(book=book2, author=book1.authors.first(), order=0)
        BookFactory(authors__author__name='ほげほげ', title='ほげほげ')
        BookFactoryWithThreeAuthors(
            authors1__author__name='Piyo Piyo', authors2__author__name='ほげほげ', authors3__author__name='ふがふが'
        )
        queryset = Author.objects.filter(bookauthorrelation__order=0).sort_by_books_count()

        # Act
        data = AuthorSerializer(queryset, many=True).data

        # Assert
        self.assertEqual(len(data), 3)
        expected_results = [
            {'name': 'Test', 'count': 2},
            {'name': 'ほげほげ', 'count': 1},
            {'name': 'Piyo Piyo', 'count': 1}
        ]
        for i in range(3):
            self.assertIn(OrderedDict(expected_results[i]), data)
