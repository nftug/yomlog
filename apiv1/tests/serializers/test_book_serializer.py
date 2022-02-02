from apiv1.tests.mixins import UserAPITestCase
from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.serializers import BookSerializer


class TestBookSerializer(UserAPITestCase):
    """BookSerializerのテストクラス (投稿)"""

    def test_create_valid(self):
        """入力データのバリデーション (正常系)"""

        """Arrange"""
        input_data = self.FIRST_BOOK_PARAMS

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)

    def test_create_valid_with_authors_blank(self):
        """入力データのバリデーション (正常系: 著者名欄が空)"""

        """Arrange"""
        input_data = {**self.FIRST_BOOK_PARAMS, 'authors': []}

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['authors'], ['不明'])

    def test_create_valid_with_authors_null(self):
        """入力データのバリデーション (正常系: 著者名欄なし)"""

        """Arrange"""
        input_data = {**self.FIRST_BOOK_PARAMS}
        del input_data['authors']

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(serializer.validated_data['authors'], ['不明'])

    def test_create_valid_with_authors_em_space(self):
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

    def test_update_valid_with_authors_changed(self):
        """部分更新時のバリデーション (正常系: 著者名の更新)"""

        """Arrange"""
        params = self.FIRST_BOOK_PARAMS
        book = self._create_dummy_book(params, self.user)
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
        params = {**self.FIRST_BOOK_PARAMS, 'authors': ['テスト太郎']}
        book = self._create_dummy_book(params, self.user)
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
        params = self.FIRST_BOOK_PARAMS
        book = self._create_dummy_book(params, self.user)
        for i in range(10):
            StatusLog.objects.create(book=book, position=i + 1, created_by=self.user)

        """Act"""
        data = BookSerializer(book).data

        """Assert"""
        self.assertEqual(len(data['status']), 10)

    def test_get_with_note(self):
        """ノート欄の取得 (正常系)"""

        """Arrange"""
        params = self.FIRST_BOOK_PARAMS
        book = self._create_dummy_book(params, self.user)
        for i in range(10):
            Note.objects.create(book=book, position=i + 1, created_by=self.user)

        """Act"""
        data = BookSerializer(book).data

        """Assert"""
        self.assertEqual(len(data['note']), 10)

    def _test_create_invalid(self, field, error, value=None, params=None, omit=False):
        """雛形: 入力データのバリデーション (異常系: 必須フィールドが不正)"""

        """Arrange"""
        params = params or self.FIRST_BOOK_PARAMS
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

        params = {**self.FIRST_BOOK_PARAMS, 'format_type': 1}
        self._test_create_invalid(
            field='total_page', value=0, error='0よりも大きな整数を入力してください。', params=params
        )

    def test_create_invalid_with_total_page_omitted(self):
        """入力データのバリデーション (異常系: Kindle本のページ量なし)"""

        params = {**self.FIRST_BOOK_PARAMS, 'format_type': 1}
        self._test_create_invalid(
            field='total_page', omit=True, error='0よりも大きな整数を入力してください。', params=params
        )

    def test_create_invalid_with_total_page_null(self):
        """入力データのバリデーション (異常系: Kindle本のページ量がnull)"""

        params = {**self.FIRST_BOOK_PARAMS, 'format_type': 1}
        self._test_create_invalid(
            field='total_page', value=None, error='0よりも大きな整数を入力してください。', params=params
        )
