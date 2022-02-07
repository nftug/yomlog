from apiv1.tests.testing import *
from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.serializers import BookSerializer
from apiv1.tests.factories import BookFactory, StatusLogFactory, NoteFactory


class TestBookSerializer(UserSerializerTestCase):
    """BookSerializerのテストクラス"""

    def test_create_valid(self):
        """入力データのバリデーション (正常系)"""

        """Arrange"""
        input_data = {**self.BOOK_FIXTURE, 'authors': ['テスト太郎']}

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)

    def test_create_valid_with_authors_blank(self):
        """入力データのバリデーション (正常系: 著者名欄が空)"""

        """Arrange"""
        input_data = {**self.BOOK_FIXTURE, 'authors': []}

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['authors'], ['不明'])

    def test_create_valid_with_authors_null(self):
        """入力データのバリデーション (正常系: 著者名欄なし)"""

        """Arrange"""
        input_data = {**self.BOOK_FIXTURE}

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['authors'], ['不明'])

    def test_create_valid_with_authors_em_space(self):
        """入力データのバリデーション(正常系: 日本語著者名欄のスペースを正規化)"""

        """Arrange"""
        input_data = {
            **self.BOOK_FIXTURE,
            'authors': ['テスト　太郎', 'テスト 太郎', 'テスト　Taro', 'Test Taro']
        }

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(
            serializer.validated_data['authors'],
            ['テスト太郎', 'テスト太郎', 'テスト Taro', 'Test Taro']
        )

    def test_update_valid_with_authors_changed(self):
        """部分更新時のバリデーション (正常系: 著者名の更新)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        input_data = {'authors': ['テスト太郎']}

        """Act"""
        serializer = BookSerializer(book, data=input_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        """Assert"""
        self.assertEqual(serializer.validated_data['authors'], ['テスト太郎'])
        self.assertEqual(BookAuthorRelation.objects.count(), 1)
        self.assertEqual(Author.objects.count(), 1)

    def test_update_valid_with_authors_empty(self):
        """部分更新時のバリデーション (正常系: 著者名が空)"""

        """Arrange"""
        book = BookFactory(
            **self.BOOK_FIXTURE, authors__author__name='テスト太郎', created_by=self.user
        )
        input_data = {'title': 'テスト'}

        """Act"""
        serializer = BookSerializer(book, data=input_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        """Assert"""
        book = Book.objects.get()
        self.assertEqual(list(book.get_author_names()), ['テスト太郎'])

    def test_create_invalid_with_title_blank(self):
        """入力データのバリデーション (異常系: タイトルが空)"""

        input_data = {**self.BOOK_FIXTURE, 'title': ''}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='title',
            error='この項目は空にできません。'
        )

    def test_create_invalid_with_title_omitted(self):
        """入力データのバリデーション (異常系: タイトルなし)"""

        input_data = {**self.BOOK_FIXTURE}
        del input_data['title']
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='title',
            error='この項目は必須です。'
        )

    def test_create_invalid_with_title_null(self):
        """入力データのバリデーション (異常系: タイトルがnull)"""

        input_data = {**self.BOOK_FIXTURE, 'title': None}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='title',
            error='この項目はnullにできません。'
        )

    def test_create_invalid_with_id_google_blank(self):
        """入力データのバリデーション (異常系: Google Books IDが空)"""

        input_data = {**self.BOOK_FIXTURE, 'id_google': ''}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='id_google',
            error='この項目は空にできません。'
        )

    def test_create_invalid_with_id_google_omitted(self):
        """入力データのバリデーション (異常系: Google Books IDなし)"""

        input_data = {**self.BOOK_FIXTURE}
        del input_data['id_google']
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='id_google',
            error='この項目は必須です。'
        )

    def test_create_invalid_with_id_google_null(self):
        """入力データのバリデーション (異常系: Google Books IDがnull)"""

        input_data = {**self.BOOK_FIXTURE, 'id_google': None}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='id_google',
            error='この項目はnullにできません。'
        )

    def test_create_invalid_with_invalid_format_type(self):
        """入力データのバリデーション (異常系: フォーマットが不正)"""

        input_data = {**self.BOOK_FIXTURE, 'format_type': 2}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='format_type',
            error='"2"は有効な選択肢ではありません。'
        )

    def test_create_invalid_with_total_zero(self):
        """入力データのバリデーション (異常系: ページ量が0)"""

        input_data = {**self.BOOK_FIXTURE, 'total': 0}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='total',
            error='0より大きな整数を入力してください。'
        )

    def test_create_invalid_with_total_omitted(self):
        """入力データのバリデーション (異常系: ページ量なし)"""

        input_data = {**self.BOOK_FIXTURE}
        del input_data['total']
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='total',
            error='この項目は必須です。'
        )

    def test_create_invalid_with_total_null(self):
        """入力データのバリデーション (異常系: ページ量がnull)"""

        input_data = {**self.BOOK_FIXTURE, 'total': None}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='total',
            error='この項目はnullにできません。'
        )

    def test_create_invalid_with_total_page_zero(self):
        """入力データのバリデーション (異常系: Kindle本のページ量が0)"""

        input_data = {**self.BOOK_FIXTURE, 'format_type': 1, 'total_page': 0}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='total_page',
            error='0より大きな整数を入力してください。'
        )

    def test_create_invalid_with_total_page_omitted(self):
        """入力データのバリデーション (異常系: Kindle本のページ量なし)"""

        input_data = {**self.BOOK_FIXTURE, 'format_type': 1}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='total_page',
            error='0より大きな整数を入力してください。'
        )

    def test_create_invalid_with_total_page_null(self):
        """入力データのバリデーション (異常系: Kindle本のページ量がnull)"""

        input_data = {**self.BOOK_FIXTURE, 'format_type': 1, 'total_page': None}
        self.serializer_invalid(
            serializer=BookSerializer, params=input_data, field='total_page',
            error='0より大きな整数を入力してください。'
        )

    def test_get_with_status(self):
        """ステータス欄の取得 (正常系)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        for i in range(10):
            StatusLogFactory(book=book, position=i + 1, created_by=self.user)

        """Act"""
        data = BookSerializer(book).data

        """Assert"""
        status = data['status']
        self.assertEqual(len(status), 10)
        expected_state_fields = ('id', 'state', 'diff', 'position', 'created_at')

        for state in status:
            for field in expected_state_fields:
                self.assertIn(field, state)

    def test_get_with_note(self):
        """ノート欄の取得 (正常系)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        for i in range(10):
            NoteFactory(book=book, position=i + 1, created_by=self.user)

        """Act"""
        data = BookSerializer(book).data

        """Assert"""
        notes = data['note']
        self.assertEqual(len(notes), 10)
        expected_note_fields = ('id', 'position', 'quote_text', 'quote_image', 'created_at')

        for note in notes:
            for field in expected_note_fields:
                self.assertIn(field, note)
