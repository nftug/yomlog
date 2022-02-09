import freezegun
from django.http import QueryDict
from django.utils.timezone import now, make_aware, datetime, timedelta
from django.test import RequestFactory

from apiv1.tests.testing import *
from apiv1.serializers import AnalyticsSerializer
from apiv1.filters import StatusLogFilter
from apiv1.tests.factories import BookFactory, CustomUserFactory, StatusLogFactory


def create_status_fixture(user):
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
        create_status_fixture(user=self.user)

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
        create_status_fixture(user=self.user)

        # Act
        data = AnalyticsSerializer(StatusLog.objects.all(), context=self.context).data

        # Assert
        result = data['pages_read']
        self.assertEqual(result['total'], 97)
        self.assertEqual(result['avg_per_day'], 25)

    def test_get_pages_read_filtered(self):
        """ページ数集計の取得 (正常系: 日付範囲フィルタ)"""

        # Arrange
        create_status_fixture(user=self.user)

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
        create_status_fixture(user=self.user)

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
        create_status_fixture(user=self.user)

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
        create_status_fixture(user=self.user)

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

    # test_get_days
    # test_get_days_with_no_status
    # test_get_days_with_break
    # test_get_days_filtered
