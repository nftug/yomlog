from django.utils.timezone import now, timedelta
from django.test import RequestFactory
from django.db.models import QuerySet

from apiv1.tests.testing import *
from apiv1.serializers import StatusLogSerializer
from apiv1.tests.factories import BookFactory, StatusLogFactory, NoteFactory


class TestStatusLogSerializer(UserSerializerTestCase):
    """StatusLogSerializerのテストクラス"""

    def setUp(self):
        super().setUp()
        self.book = BookFactory(created_by=self.user)
        self.request = RequestFactory().get('/')
        self.context = {'request': self.request}

    def test_create_valid(self):
        """入力データのバリデーション (正常系)"""

        # Arrange
        input_data = {'book': self.book.id, 'position': 1}
        self.request.user = self.user

        # Act
        serializer = StatusLogSerializer(data=input_data, context=self.context)

        # Assert
        self.assertEqual(serializer.is_valid(), True)

    def test_create_invalid_position_blank(self):
        """入力データのバリデーション (異常系: positionが空)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': ''}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='position', context=self.context,
            error='有効な整数を入力してください。'
        )

    def test_create_invalid_position_null(self):
        """入力データのバリデーション (異常系: positionがnull)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': None}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='position', context=self.context,
            error='この項目はnullにできません。'
        )

    def test_create_invalid_position_omit(self):
        """入力データのバリデーション (異常系: positionなし)"""

        self.request.user = self.user
        input_data = {'book': self.book.id}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='position', context=self.context,
            error='この項目は必須です。'
        )

    def test_create_invalid_position_less_than_zero(self):
        """入力データのバリデーション (異常系: positionが0以下)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': -1}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='position', context=self.context,
            error='0以上の整数を入力してください。'
        )

    def test_create_invalid_position_larger_than_total(self):
        """入力データのバリデーション (異常系: positionが書籍のtotalよりも大きい)"""

        self.request.user = self.user
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        input_data = {'book': book.id, 'position': 120}

        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='position', context=self.context,
            error='位置の指定が不正です。'
        )

    def test_create_invalid_book_blank(self):
        """入力データのバリデーション (異常系: bookが空)"""

        self.request.user = self.user
        input_data = {'book': '', 'position': 10}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='book', context=self.context,
            error='この項目はnullにできません。'
        )

    def test_create_invalid_book_null(self):
        """入力データのバリデーション (異常系: bookがnull)"""

        self.request.user = self.user
        input_data = {'book': None, 'position': 10}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='book', context=self.context,
            error='この項目はnullにできません。'
        )

    def test_create_invalid_book_omit(self):
        """入力データのバリデーション (異常系: bookなし)"""

        self.request.user = self.user
        input_data = {'position': 10}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='book', context=self.context,
            error='この項目は必須です。'
        )

    def test_create_invalid_book_invalid_user(self):
        """入力データのバリデーション (異常系: bookが他ユーザーのものを指定)"""

        self.request.user = self.user
        book = BookFactory(created_by=self.user2)
        input_data = {'book': book.id, 'position': 10}
        self.serializer_invalid(
            serializer=StatusLogSerializer, params=input_data, field='book', context=self.context,
            error='自ユーザーが作成した本を選択してください。'
        )

    def test_get_state(self):
        """ステータスの取得 (正常系)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        StatusLogFactory(book=book, position=1, created_by=self.user)
        state = StatusLogFactory(
            book=book, position=32, created_by=self.user, created_at=now() + timedelta(seconds=1)
        )

        # Act
        data = StatusLogSerializer(state).data

        # Assert
        expected_dict = {
            'id': str(state.id),
            'state': 'reading',
            'diff': {'value': 31, 'percentage': 28, 'page': 31},
            'position': {'value': 32, 'percentage': 29, 'page': 32},
            'created_at': convert_time_into_json_str(state.created_at),
        }
        self.assert_book_included_dict(data, expected_dict, book)

    def test_get_state_first_record(self):
        """ステータスの取得 (正常系: 初回の記録)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        state = StatusLogFactory(
            book=book, position=32, created_by=self.user, created_at=now() + timedelta(seconds=1)
        )

        # Act
        data = StatusLogSerializer(state).data

        # Assert
        expected_dict = {
            'id': str(state.id),
            'state': 'reading',
            'diff': {'value': 32, 'percentage': 29, 'page': 32},
            'position': {'value': 32, 'percentage': 29, 'page': 32},
            'created_at': convert_time_into_json_str(state.created_at),
        }
        self.assert_book_included_dict(data, expected_dict, book)

    def test_get_state_to_be_read(self):
        """ステータスの取得 (正常系: 積読状態)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        StatusLogFactory(book=book, position=32, created_by=self.user)
        state = StatusLogFactory(
            book=book, position=0, created_by=self.user, created_at=now() + timedelta(seconds=1)
        )

        # Act
        data = StatusLogSerializer(state).data

        # Assert
        expected_dict = {
            'id': str(state.id),
            'state': 'to_be_read',
            'diff': {'value': 0, 'percentage': 0, 'page': 0},
            'position': {'value': 32, 'percentage': 29, 'page': 32},
            'created_at': convert_time_into_json_str(state.created_at),
        }
        self.assert_book_included_dict(data, expected_dict, book)

    def test_get_state_read(self):
        """ステータスの取得 (正常系: 読了状態)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        StatusLogFactory(book=book, position=32, created_by=self.user)
        state = StatusLogFactory(
            book=book, position=110, created_by=self.user, created_at=now() + timedelta(seconds=1)
        )

        # Act
        data = StatusLogSerializer(state).data

        # Assert
        expected_dict = {
            'id': str(state.id),
            'state': 'read',
            'diff': {'value': 78, 'percentage': 70, 'page': 78},
            'position': {'value': 110, 'percentage': 100, 'page': 110},
            'created_at': convert_time_into_json_str(state.created_at),
        }
        self.assert_book_included_dict(data, expected_dict, book)

    def test_get_state_minus(self):
        """ステータスの取得 (正常系: マイナスの進捗)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        StatusLogFactory(book=book, position=32, created_by=self.user)
        state = StatusLogFactory(
            book=book, position=31, created_by=self.user, created_at=now() + timedelta(seconds=1)
        )

        # Act
        data = StatusLogSerializer(state).data

        # Assert
        expected_dict = {
            'id': str(state.id),
            'state': 'reading',
            'diff': {'value': 0, 'percentage': 0, 'page': 0},
            'position': {'value': 31, 'percentage': 28, 'page': 31},
            'created_at': convert_time_into_json_str(state.created_at),
        }
        self.assert_book_included_dict(data, expected_dict, book)

    def test_get_state_after_zero(self):
        """ステータスの取得 (正常系: 積読状態からの復帰)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        StatusLogFactory(book=book, position=1, created_by=self.user)
        StatusLogFactory(book=book, position=0, created_by=self.user)
        StatusLogFactory(book=book, position=0, created_by=self.user)
        state = StatusLogFactory(
            book=book, position=32, created_by=self.user, created_at=now() + timedelta(seconds=1)
        )

        # Act
        data = StatusLogSerializer(state).data

        # Assert
        expected_dict = {
            'id': str(state.id),
            'state': 'reading',
            'diff': {'value': 31, 'percentage': 28, 'page': 31},
            'position': {'value': 32, 'percentage': 29, 'page': 32},
            'created_at': convert_time_into_json_str(state.created_at),
        }
        self.assert_book_included_dict(data, expected_dict, book)

    def test_get_state_ebook(self):
        """ステータスの取得 (正常系: Kindle本の位置Noをページ数に変換)"""

        # Arrange
        book = BookFactory(total=2500, total_page=220, format_type=1, created_by=self.user)
        StatusLogFactory(book=book, position=120, created_by=self.user)
        state = StatusLogFactory(
            book=book, position=1111, created_by=self.user, created_at=now() + timedelta(seconds=1)
        )

        # Act
        data = StatusLogSerializer(state).data

        # Assert
        expected_dict = {
            'id': str(state.id),
            'state': 'reading',
            'diff': {'value': 991, 'percentage': 39, 'page': 88},
            'position': {'value': 1111, 'percentage': 44, 'page': 98},
            'created_at': convert_time_into_json_str(state.created_at),
        }
        self.assert_book_included_dict(data, expected_dict, book)
