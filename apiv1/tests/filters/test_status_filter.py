from datetime import datetime
from django.http import QueryDict
from django.utils.timezone import make_aware
from datetime import datetime

from backend.models import Book
from apiv1.tests.testing import *
from apiv1.filters import StatusLogFilter
from apiv1.tests.factories import BookFactory, BookFactoryWithThreeAuthors, StatusLogFactory


class TestStatusLogFilter(UserAPITestCase):
    """進捗フィルタのテストクラス"""

    def test_filter_created_at(self):
        """作成日による絞り込み (正常系)"""

        # Arrange
        state_first = StatusLogFactory(created_at=make_aware(datetime(2022, 1, 1)), created_by=self.user)
        state_second = StatusLogFactory(created_at=make_aware(datetime(2022, 1, 3)), created_by=self.user)
        qd = QueryDict('created_at_after=2022-01-01&created_at_before=2022-01-02')

        # Act
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, state_first.id)

    def test_filter_to_be_read(self):
        """ステータス名で絞り込み (正常系: to_be_read)"""

        # Arrange
        state_first = StatusLogFactory(position=1, created_by=self.user)
        state_second = StatusLogFactory(position=0, created_by=self.user)
        qd = QueryDict('state=to_be_read')

        # Act
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, state_second.id)

    def test_filter_reading(self):
        """ステータス名で絞り込み (正常系: reading)"""

        # Arrange
        state_first = StatusLogFactory(position=1, created_by=self.user)
        state_second = StatusLogFactory(position=0, created_by=self.user)
        qd = QueryDict('state=reading')

        # Act
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, state_first.id)

    def test_filter_read(self):
        """ステータス名で絞り込み (正常系: read)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        state_first = StatusLogFactory(position=1, created_by=self.user)
        state_second = StatusLogFactory(position=110, created_by=self.user)
        qd = QueryDict('state=read')

        # Act
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, state_second.id)

    def test_filter_all(self):
        """ステータス名で絞り込み (正常系: all)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        state_first = StatusLogFactory(position=1, created_by=self.user)
        state_second = StatusLogFactory(position=110, created_by=self.user)
        qd = QueryDict('state=all')

        # Act
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 2)

    def test_filter_not_reading(self):
        """ステータス名で絞り込み (正常系: not reading)"""

        # Arrange
        state_first = StatusLogFactory(position=1, created_by=self.user)
        state_second = StatusLogFactory(position=0, created_by=self.user)
        qd = QueryDict('state_not=to_be_read')

        # Act
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, state_first.id)

    def test_filter_invalid_state(self):
        """ステータス名で絞り込み (異常系: 不正なステータス名)"""

        # Arrange
        qd = QueryDict('state=hoge')

        # Act
        filterset = StatusLogFilter(qd, queryset=StatusLog.objects.all())

        # Assert
        self.assertNotEqual(filterset.is_valid, True)
