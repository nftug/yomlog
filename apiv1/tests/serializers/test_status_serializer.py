from django.test import RequestFactory

from apiv1.tests.testing import *
from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
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
