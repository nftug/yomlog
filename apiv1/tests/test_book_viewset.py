from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation


class UserAPITestCase(APITestCase):
    """APITestCase (ユーザー認証)"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ログインユーザーを初期登録
        cls.user = get_user_model().objects.create_user(
            username='user',
            email='user@example.com',
            password='secret'
        )
        cls.user2 = get_user_model().objects.create_user(
            username='user2',
            email='user2@example.com',
            password='secret'
        )


class BookViewSetTestCase(UserAPITestCase):
    """雛形: BookViewSetのテストクラス"""

    TARGET_URL = '/api/v1/book/'
    TARGET_URL_WITH_PK = '/api/v1/book/{}/'
    DUMMY_THUMBNAIL_URL = 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=No+Image'

    def setUp(self):
        """setUpメソッド"""

        super().setUp()
        self.FIRST_BOOK_PARAMS = {
            'title': 'test',
            'authors': ['author 1', 'author 2'],
            'id_google': 'xxx',
            'thumbnail': None,
            'format_type': 0,
            'total': 100,
            'total_page': None,
            'amazon_dp': None
        }
        self.SECOND_BOOK_PARAMS = {
            'id_google': 'yyy',
            'title': 'test updated',
            'authors': ['author 1', 'author 2', 'author 3'],
            'format_type': 1,
            'total': 2000
        }

    def _create_dummy_book(self, params):
        """書籍のダミーデータを作成"""

        dummy_book_params = {**params}
        del dummy_book_params['authors']
        book = Book.objects.create(**dummy_book_params, created_by=self.user)

        for (i, author_name) in enumerate(params['authors']):
            author = Author.objects.create(name=author_name)
            BookAuthorRelation.objects.create(order=i, book=book, author=author)

        return book

    def _get_expected_json(self, params, book):
        """Assert対象のJSONデータを生成"""

        if 'authors' in params:
            authors_expected = [_ for _ in params['authors']]
        else:
            authors_expected = [_ for _ in book.get_author_names()]

        expected_json = {
            'id': str(book.id),
            'status': [],
            'note': [],
            'title': params.get('title') or book.title,
            'authors': authors_expected,
            'id_google': params.get('id_google') or book.id_google,
            'thumbnail': params.get('thumbnail') or book.thumbnail or self.DUMMY_THUMBNAIL_URL,
            'format_type': params.get('format_type') or book.format_type,
            'total': params.get('total') or book.total,
            'total_page': params.get('total_page') or book.total_page,
            'amazon_dp': params.get('amazon_dp') or book.amazon_dp,
            'created_at': str(localtime(book.created_at)).replace(' ', 'T')
        }

        return expected_json


class TestBookCreateAPIView(BookViewSetTestCase):
    """BookViewSetのテストクラス (POST)"""

    def test_create_success(self):
        """登録APIへのPOSTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)

        """Act"""
        params = self.FIRST_BOOK_PARAMS
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

        book = Book.objects.get()
        expected_json = self._get_expected_json(params, book)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_failure_existed(self):
        """登録APIへのPOSTリクエスト (異常系: Google Books IDの重複)"""

        """Arrange"""
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS)
        self.client.force_authenticate(user=self.user)

        """Act"""
        params = {
            **self.SECOND_BOOK_PARAMS,
            'id_google': self.FIRST_BOOK_PARAMS['id_google']
        }
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        book = Book.objects.get()
        expected_json = self._get_expected_json({}, book)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_failure_validation(self):
        """登録APIへのPOSTリクエスト (異常系: バリデーションNG)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)

        """Act"""
        params = {
            **self.FIRST_BOOK_PARAMS,
            'title': ''
        }
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(Book.objects.count(), 0)
        self.assertEqual(response.status_code, 400)

    def test_create_failure_no_auth(self):
        """登録APIへのPOSTリクエスト (異常系: 認証なし)"""

        """Arrange"""

        """Act"""
        params = self.FIRST_BOOK_PARAMS
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(Book.objects.count(), 0)
        self.assertEqual(response.status_code, 401)


class TestBookUpdateAPIView(BookViewSetTestCase):
    """BookViewSetのテストクラス (PATCH/PUT)"""

    """PUT"""

    def test_put_success(self):
        """登録APIへのPUTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS)

        """Act"""
        params = {
            **self.SECOND_BOOK_PARAMS,
            'id': book.id
        }
        response = self.client.put(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        book = Book.objects.get()
        expected_json = self._get_expected_json(params, book)
        self.assertJSONEqual(response.content, expected_json)

    def test_put_failure_validation(self):
        """登録APIへのPUTリクエスト (異常系: バリデーションNG)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS)

        """Act"""
        params = {}
        response = self.client.put(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 400)

    def test_put_failure_invalid_auth(self):
        """登録APIへのPUTリクエスト (異常系: 異なるユーザーによる権限エラー)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS)

        """Act"""
        params = {
            **self.SECOND_BOOK_PARAMS,
            'id': book.id
        }
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)

    """PATCH"""

    def _test_patch_success(self, authors):
        """雛形: 登録APIへのPATCHリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS)

        """Act"""
        params = {'title': 'test updated'}
        if authors:
            params['authors'] = authors

        response = self.client.patch(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        book = Book.objects.get()
        expected_json = self._get_expected_json(params, book)
        self.assertJSONEqual(response.content, expected_json)

    def test_patch_success_with_authors(self):
        """登録APIへのPATCHリクエスト (正常系: 著者欄あり)"""

        authors = ['author 1', 'author 2', 'author 3']
        self._test_patch_success(authors)

    def test_patch_success_no_authors(self):
        """登録APIへのPATCHリクエスト (正常系: 著者欄なし)"""

        self._test_patch_success(None)

    def test_put_failure_invalid_auth(self):
        """登録APIへのPATCHリクエスト (異常系: 異なるユーザーによる権限エラー)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS)

        """Act"""
        self.client.force_authenticate(user=self.user2)
        params = {'title': 'test updated'}
        response = self.client.patch(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)

# TODO: RetrieveとListとDeleteのテストの実装
