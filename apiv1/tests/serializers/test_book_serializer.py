from apiv1.tests.mixins import UserAPITestCase
from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.serializers import BookSerializer


class TestBookPostSerializer(UserAPITestCase):
    """BookSerializerのテストクラス (投稿)"""

    def test_create_valid(self):
        """入力データのバリデーション (正常系)"""

        """Arrange"""
        input_data = self.FIRST_BOOK_PARAMS

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)

    def test_create_valid_with_author_blank(self):
        """入力データのバリデーション (正常系: 著者名欄が空)"""

        """Arrange"""
        input_data = {**self.FIRST_BOOK_PARAMS, 'authors': []}

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['authors'], ['不明'])

    def test_create_valid_with_author_null(self):
        """入力データのバリデーション (正常系: 著者名欄なし)"""

        """Arrange"""
        input_data = {**self.FIRST_BOOK_PARAMS}
        del input_data['authors']

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['authors'], ['不明'])

    def test_create_valid_with_author_em_space(self):
        """入力データのバリデーション(正常系: 日本語著者名欄のスペースを正規化)"""

        """Arrange"""
        input_data = {
            **self.FIRST_BOOK_PARAMS,
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

    def test_create_invalid_with_title_blank(self):
        """入力データのバリデーション (異常系: タイトルが空)"""

        """Arrange"""
        input_data = {
            **self.FIRST_BOOK_PARAMS,
            'title': ''
        }

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['title'])
        self.assertCountEqual(
            [str(x) for x in serializer.errors['title']],
            ['この項目は空にできません。']
        )

    def test_update_valid_with_authors_changed(self):
        """部分更新時のバリデーション (正常系: 著者名の更新)"""

        """Arrange"""
        params = self.FIRST_BOOK_PARAMS
        book = self._create_dummy_book(params, self.user)
        input_data = {'authors': ['テスト太郎']}

        """Act"""
        serializer = BookSerializer(book, data=input_data, partial=True)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['authors'], ['テスト太郎'])

    def test_update_valid_with_authors_empty(self):
        """部分更新時のバリデーション (正常系: 著者名が空)"""

        """Arrange"""
        params = {**self.FIRST_BOOK_PARAMS, 'authors': ['テスト太郎']}
        book = self._create_dummy_book(params, self.user)
        input_data = {'title': 'テスト'}

        """Act"""
        serializer = BookSerializer(book, data=input_data, partial=True)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        book: Book = Book.objects.get()
        self.assertEqual(list(book.get_author_names()), ['テスト太郎'])
