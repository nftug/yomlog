from django.utils.timezone import now, timedelta
from django.test import RequestFactory
from django.db.models import QuerySet

from apiv1.tests.testing import *
from backend.models import Book, Note, Author, BookAuthorRelation
from apiv1.serializers import NoteSerializer
from apiv1.tests.factories import BookFactory, NoteFactory


class TestNoteSerializer(UserSerializerTestCase):
    """NoteSerializerのテストクラス"""

    def setUp(self):
        super().setUp()
        self.book = BookFactory(created_by=self.user)
        self.request = RequestFactory().get('/')
        self.context = {'request': self.request}

    def test_create_valid(self):
        """入力データのバリデーション (正常系)"""

        # Arrange
        input_data = {'book': self.book.id, 'position': 1, 'content': 'ほげほげ'}
        self.request.user = self.user

        # Act
        serializer = NoteSerializer(data=input_data, context=self.context)

        # Assert
        self.assertEqual(serializer.is_valid(), True)

    def test_create_invalid_position_blank(self):
        """入力データのバリデーション (異常系: positionが空)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': '', 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='position', context=self.context,
            error='有効な整数を入力してください。'
        )

    def test_create_invalid_position_null(self):
        """入力データのバリデーション (異常系: positionがnull)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': None, 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='position', context=self.context,
            error='この項目はnullにできません。'
        )

    def test_create_invalid_position_omit(self):
        """入力データのバリデーション (異常系: positionなし)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='position', context=self.context,
            error='この項目は必須です。'
        )

    def test_create_invalid_position_less_than_zero(self):
        """入力データのバリデーション (異常系: positionが0以下)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': -1, 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='position', context=self.context,
            error='0以上の整数を入力してください。'
        )

    def test_create_invalid_position_larger_than_total(self):
        """入力データのバリデーション (異常系: positionが書籍のtotalよりも大きい)"""

        self.request.user = self.user
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        input_data = {'book': book.id, 'position': 120, 'content': 'ほげほげ'}

        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='position', context=self.context,
            error='位置の指定が不正です。'
        )

    def test_create_invalid_book_blank(self):
        """入力データのバリデーション (異常系: bookが空)"""

        self.request.user = self.user
        input_data = {'book': '', 'position': 10, 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='book', context=self.context,
            error='この項目はnullにできません。'
        )

    def test_create_invalid_book_null(self):
        """入力データのバリデーション (異常系: bookがnull)"""

        self.request.user = self.user
        input_data = {'book': None, 'position': 10, 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='book', context=self.context,
            error='この項目はnullにできません。'
        )

    def test_create_invalid_book_omit(self):
        """入力データのバリデーション (異常系: bookなし)"""

        self.request.user = self.user
        input_data = {'position': 10, 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='book', context=self.context,
            error='この項目は必須です。'
        )

    def test_create_invalid_book_invalid_user(self):
        """入力データのバリデーション (異常系: bookが他ユーザーのものを指定)"""

        self.request.user = self.user
        book = BookFactory(created_by=self.user2)
        input_data = {'book': book.id, 'position': 10, 'content': 'ほげほげ'}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='book', context=self.context,
            error='自ユーザーが作成した本を選択してください。'
        )

    def test_create_invalid_content_blank(self):
        """入力データのバリデーション (異常系: contentが空)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': 10, 'content': ''}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='content', context=self.context,
            error='この項目は空にできません。'
        )

    def test_create_invalid_content_null(self):
        """入力データのバリデーション (異常系: contentがnull)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': 10, 'content': None}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='content', context=self.context,
            error='この項目はnullにできません。'
        )

    def test_create_invalid_content_omit(self):
        """入力データのバリデーション (異常系: contentなし)"""

        self.request.user = self.user
        input_data = {'book': self.book.id, 'position': 10}
        self.serializer_invalid(
            serializer=NoteSerializer, params=input_data, field='content', context=self.context,
            error='この項目は必須です。'
        )

    def test_get_note(self):
        """ノートの取得 (正常系)"""

        # Arrange
        book = BookFactory(total=110, format_type=0, created_by=self.user)
        note = NoteFactory(**self.NOTE_FIXTURE, book=book, created_by=self.user)

        # Act
        data = NoteSerializer(note).data

        # Assert
        expected_dict = get_expected_note_json(self.NOTE_FIXTURE, note)
        self.assert_book_included_dict(data, expected_dict, book)
