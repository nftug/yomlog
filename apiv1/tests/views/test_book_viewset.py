from django.utils.timezone import now, timedelta

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.tests.mixins import *


class BookViewSetTestCase(UserAPITestCase):
    """雛形: BookViewSetのテストクラス"""

    TARGET_URL = '/api/v1/book/'
    TARGET_URL_WITH_PK = '/api/v1/book/{}/'


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
        expected_json = get_expected_book_json(params, book)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_failure_existed_gid(self):
        """登録APIへのPOSTリクエスト (異常系: Google Books IDの重複)"""

        """Arrange"""
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)
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
        expected_json = get_expected_book_json({}, book)
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

    def test_put_success(self):
        """登録APIへのPUTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)

        """Act"""
        params = {
            **self.SECOND_BOOK_PARAMS,
            'id': book.id
        }
        response = self.client.put(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        book = Book.objects.get()
        expected_json = get_expected_book_json(params, book)
        self.assertJSONEqual(response.content, expected_json)

    def test_put_failure_validation(self):
        """登録APIへのPUTリクエスト (異常系: バリデーションNG)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)

        """Act"""
        params = {}
        response = self.client.put(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 400)

    def test_put_failure_invalid_user(self):
        """登録APIへのPUTリクエスト (異常系: 異なるユーザーによる権限エラー)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)

        """Act"""
        params = {
            **self.SECOND_BOOK_PARAMS,
            'id': book.id
        }
        self.client.force_authenticate(user=self.user2)
        response = self.client.put(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)

    def test_patch_success(self):
        """雛形: 登録APIへのPATCHリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)

        """Act"""
        params = {'title': 'test updated'}

        response = self.client.patch(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        book = Book.objects.get()
        expected_json = get_expected_book_json(params, book)
        self.assertJSONEqual(response.content, expected_json)


class TestBookRetrieveAPIView(BookViewSetTestCase):
    """BookViewSetのテストクラス (Retrieve)"""

    def test_retrieve_success(self):
        """APIへのGETリクエスト [Retrieve] (正常系)"""

        """Arrange"""
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)
        self.client.force_authenticate(user=self.user)

        """"Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(book.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        expected_json = get_expected_book_json({}, book)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_failure_invalid_user(self):
        """APIへのGETリクエスト [Retrieve] (異常系: 異なるユーザーによる権限エラー)"""

        """Arrange"""
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)
        self.client.force_authenticate(user=self.user2)

        """"Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(book.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)

    def test_retrieve_failure_no_auth(self):
        """APIへのGETリクエスト [Retrieve] (異常系: 認証なし)"""

        """Arrange"""
        book = create_dummy_book(params=self.FIRST_BOOK_PARAMS, user=self.user)

        """"Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(book.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)


class TestBookListAPIView(BookViewSetTestCase):
    """BookViewSetのテストクラス (List)"""

    def test_list_success(self):
        """APIへのGETリクエスト [List] (正常系)"""

        """Arrange"""
        books = create_dummy_books(n=10, params=self.FIRST_BOOK_PARAMS, user=self.user)

        self.client.force_authenticate(user=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), len(books))

        for i in range(10):
            self.assertEqual_result_with_book(result=results[i], book=books[i])

    def test_list_success_pagination(self):
        """APIへのGETリクエスト [List] (正常系: ページネーション)"""

        """Arrange"""
        books = create_dummy_books(n=13, params=self.FIRST_BOOK_PARAMS, user=self.user)

        self.client.force_authenticate(user=self.user)

        """Act"""
        params = {'page': 2}
        response = self.client.get(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = list(response.data['results'])
        self.assertEqual(len(results), 1)

        self.assertEqual_result_with_book(result=results[0], book=books[-1])

    def test_list_success_exclude_other_users(self):
        """APIへのGETリクエスト [List] (正常系: 自ユーザー作成のデータのみ表示)"""

        """Arrange"""
        books = create_dummy_books(n=10, params=self.FIRST_BOOK_PARAMS, user=self.user)
        # 最後の一件のみ、レコードの作成者をuser2に設定する
        books[-1].created_by = self.user2
        books[-1].save()

        self.client.force_authenticate(user=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = list(response.data['results'])
        self.assertEqual(len(results), len(books) - 1)

        books.pop()
        for i in range(9):
            self.assertEqual_result_with_book(result=results[i], book=books[i])

    def test_list_success_sort_by_accessed_at(self):
        """APIへのGETリクエスト [List] (正常系: アクセス日時でソート)"""

        """Arrange"""
        books = create_dummy_books(n=10, params=self.FIRST_BOOK_PARAMS, user=self.user)

        # 最初に作成した本に対してステータスを記録する
        StatusLog.objects.create(
            book=books[-1], position=10, created_by=self.user, created_at=now() + timedelta(days=1)
        )
        # 2番目に作成した本に対してノートを記録 (ソートには影響なしを想定)
        Note.objects.create(
            book=books[-2], position=10, created_by=self.user, created_at=now() + timedelta(days=2)
        )

        self.client.force_authenticate(user=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = list(response.data['results'])
        self.assertEqual(len(results), len(books))

        # 結果にのみstatusの中身が加わっているので、そのままだと検証に失敗する
        # →idのみ検証
        self.assertEqual(results[0]['id'], str(books[-1].id))

    def test_list_failure_no_auth(self):
        """APIへのGETリクエスト [List] (異常系: 認証なし)"""

        """Arrange"""
        create_dummy_books(n=10, params=self.FIRST_BOOK_PARAMS, user=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)


class TestBookDeleteAPIView(BookViewSetTestCase):
    """BookViewSetのテストクラス (DELETE)"""

    def test_delete_success(self):
        """APIへのDELETEリクエスト (正常系)"""

        """Arrange"""
        book = create_dummy_book(self.FIRST_BOOK_PARAMS, user=self.user)
        self.client.force_authenticate(user=self.user)

        """Act"""
        params = self.FIRST_BOOK_PARAMS
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(Book.objects.count(), 0)
        self.assertEqual(BookAuthorRelation.objects.count(), 0)
        self.assertEqual(Author.objects.count(), 0)
        self.assertEqual(response.status_code, 204)

    def test_delete_failure_invalid_user(self):
        """APIへのDELETEリクエスト (異常系: 他ユーザーのデータの削除不可)"""

        """Arrange"""
        book = create_dummy_book(self.FIRST_BOOK_PARAMS, user=self.user)
        self.client.force_authenticate(user=self.user2)

        """Act"""
        params = self.FIRST_BOOK_PARAMS
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(response.status_code, 404)

    def test_delete_failure_no_auth(self):
        """APIへのDELETEリクエスト (異常系: 認証なし)"""

        """Arrange"""
        book = create_dummy_book(self.FIRST_BOOK_PARAMS, user=self.user)

        """Act"""
        params = self.FIRST_BOOK_PARAMS
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(book.id), params, format='json')

        """Assert"""
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(response.status_code, 401)
