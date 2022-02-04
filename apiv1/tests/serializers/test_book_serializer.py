from apiv1.tests.testing import *
from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.serializers import BookSerializer
from apiv1.tests.factories import BookFactory, StatusLogFactory, NoteFactory


class TestBookSerializer(UserAPITestCase):
    """BookSerializerのテストクラス (投稿)"""

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

        for state in status:
            self.assertEqual('id' in state, True)
            self.assertEqual('state' in state, True)
            self.assertEqual('diff' in state, True)
            self.assertEqual('position' in state, True)
            self.assertEqual('created_at' in state, True)
            self.assertNotEqual('created_by' in state, True)

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

        for note in notes:
            self.assertEqual('id' in note, True)
            self.assertEqual('position' in note, True)
            self.assertEqual('quote_text' in note, True)
            self.assertEqual('quote_image' in note, True)
            self.assertEqual('created_at' in note, True)
            self.assertEqual('created_at' in note, True)
            self.assertNotEqual('created_by' in note, True)

    def _test_create_invalid(self, field, error, value=None, params=None, omit=False):
        """雛形: 入力データのバリデーション (異常系: 必須フィールドが不正)"""

        """Arrange"""
        params = params or self.BOOK_FIXTURE
        input_data = {**params}

        if omit:
            del input_data[field]
        else:
            input_data = {**params, field: value}

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), [field])
        self.assertCountEqual(
            [str(x) for x in serializer.errors[field]],
            [error]
        )

    def test_create_invalid_with_title_blank(self):
        """入力データのバリデーション (異常系: タイトルが空)"""

        self._test_create_invalid(
            field='title', value='', error='この項目は空にできません。'
        )

    def test_create_invalid_with_title_omitted(self):
        """入力データのバリデーション (異常系: タイトルなし)"""

        self._test_create_invalid(
            field='title', omit=True, error='この項目は必須です。'
        )

    def test_create_invalid_with_title_null(self):
        """入力データのバリデーション (異常系: タイトルがnull)"""

        self._test_create_invalid(
            field='title', value=None, error='この項目はnullにできません。'
        )

    def test_create_invalid_with_id_google_blank(self):
        """入力データのバリデーション (異常系: Google Books IDが空)"""

        self._test_create_invalid(
            field='id_google', value='', error='この項目は空にできません。'
        )

    def test_create_invalid_with_id_google_omitted(self):
        """入力データのバリデーション (異常系: Google Books IDなし)"""

        self._test_create_invalid(
            field='id_google', omit=True, error='この項目は必須です。'
        )

    def test_create_invalid_with_id_google_null(self):
        """入力データのバリデーション (異常系: Google Books IDがnull)"""

        self._test_create_invalid(
            field='id_google', value=None, error='この項目はnullにできません。'
        )

    def test_create_invalid_with_invalid_format_type(self):
        """入力データのバリデーション (異常系: フォーマットが不正)"""

        self._test_create_invalid(
            field='format_type', value=2, error='"2"は有効な選択肢ではありません。'
        )

    def test_create_invalid_with_total_zero(self):
        """入力データのバリデーション (異常系: ページ量が0)"""

        self._test_create_invalid(
            field='total', value=0, error='0よりも大きな整数を入力してください。'
        )

    def test_create_invalid_with_total_omitted(self):
        """入力データのバリデーション (異常系: ページ量なし)"""

        self._test_create_invalid(
            field='total', omit=True, error='この項目は必須です。'
        )

    def test_create_invalid_with_total_null(self):
        """入力データのバリデーション (異常系: ページ量がnull)"""

        self._test_create_invalid(
            field='total', value=None, error='この項目はnullにできません。'
        )

    def test_create_invalid_with_total_page_zero(self):
        """入力データのバリデーション (異常系: Kindle本のページ量が0)"""

        params = {**self.BOOK_FIXTURE, 'format_type': 1, 'total_page': 100}
        self._test_create_invalid(
            field='total_page', value=0, error='0よりも大きな整数を入力してください。', params=params
        )

    def test_create_invalid_with_total_page_omitted(self):
        """入力データのバリデーション (異常系: Kindle本のページ量なし)"""

        params = {**self.BOOK_FIXTURE, 'format_type': 1, 'total_page': 100}
        self._test_create_invalid(
            field='total_page', omit=True, error='0よりも大きな整数を入力してください。', params=params
        )

    def test_create_invalid_with_total_page_null(self):
        """入力データのバリデーション (異常系: Kindle本のページ量がnull)"""

        params = {**self.BOOK_FIXTURE, 'format_type': 1, 'total_page': 100}
        self._test_create_invalid(
            field='total_page', value=None, error='0よりも大きな整数を入力してください。', params=params
        )
