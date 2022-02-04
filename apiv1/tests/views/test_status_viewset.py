from django.utils.timezone import now, timedelta

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.tests.mixins import *
from apiv1.tests.factries import BookFactory, StatusLogFactory, create_dummy_status


class StatusLogTestCase(UserAPITestCase):
    """雛形: StatusLogViewsetのテストクラス"""

    TARGET_URL = '/api/v1/status/'
    TARGET_URL_WITH_PK = '/api/v1/status/{}/'


class TestStatusLogCreateAPIView(StatusLogTestCase):
    """StatusLogViewSetのテストクラス (POST)"""

    def test_create_success(self):
        """POSTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        params = {**self.STATUS_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(StatusLog.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

        state = StatusLog.objects.get()
        expected_json = get_expected_state_json(params, state)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_failure_invalid_user(self):
        """登録APIへのPOSTリクエスト (異常系: バリデーションNG)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user2)
        params = {**self.STATUS_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 400)
        self.assertEqual(StatusLog.objects.count(), 0)

    def test_create_failure_no_auth(self):
        """登録APIへのPOSTリクエスト (異常系: 認証なし)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        params = {**self.STATUS_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)
        self.assertEqual(StatusLog.objects.count(), 0)


class TestStatusLogUpdateAPIView(StatusLogTestCase):
    """StatusLogViewSetのテストクラス (PUT/PATCH)"""

    def test_put_success(self):
        """PUTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        state = StatusLogFactory(book=book, created_by=self.user)
        params = {**self.STATUS_FIXTURE, 'id': state.id, 'book': book.id, 'position': 100}

        """Act"""
        response = self.client.put(self.TARGET_URL_WITH_PK.format(state.id), params, format='json')

        """Assert"""
        self.assertEqual(StatusLog.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        state = StatusLog.objects.get()
        expected_json = get_expected_state_json(params, state)
        self.assertJSONEqual(response.content, expected_json)

    def test_patch_success(self):
        """PATCHリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        state = StatusLogFactory(book=book, created_by=self.user)
        params = {'position': 100}

        """Act"""
        response = self.client.patch(self.TARGET_URL_WITH_PK.format(state.id), params, format='json')

        """Assert"""
        self.assertEqual(StatusLog.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        state = StatusLog.objects.get()
        expected_json = get_expected_state_json(params, state)
        self.assertJSONEqual(response.content, expected_json)


class TestStatusLogRetrieveAPIView(StatusLogTestCase):
    """StatusLogViewSetのテストクラス (Retrieve)"""

    def test_retrieve_success(self):
        """GETリクエスト [Retrieve] (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        state = StatusLogFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        expected_json = get_expected_state_json({}, state)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_failure_invalid_user(self):
        """GETリクエスト [Retrieve] (異常系: 異なるユーザーによる権限エラー)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user2)
        state = StatusLogFactory(book=book, created_by=self.user2)

        """Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)

    def test_retrieve_failure_no_auth(self):
        """GETリクエスト [Retrieve] (異常系: 認証なし)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        state = StatusLogFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)


class TestStatusLogListAPIView(StatusLogTestCase):
    """StatusLogViewSetのテストクラス (List)"""

    def test_list_success(self):
        """GETリクエスト [List] (正常系: 作成日時で降順ソート)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        status = create_dummy_status({**self.STATUS_FIXTURE, 'created_by': self.user}, 10)

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), len(status))

        for i in range(10):
            result_id, state_id = results[i]['id'], str(status[i].id)
            self.assertEqual(result_id, state_id)

    def test_list_success_pagination(self):
        """GETリクエスト [List] (正常系: ページネーション)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        status = create_dummy_status({**self.STATUS_FIXTURE, 'created_by': self.user}, 13)
        params = {'page': 2}

        """Act"""
        response = self.client.get(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), 1)

        result_id, state_id = results[0]['id'], str(status[-1].id)
        self.assertEqual(result_id, state_id)


class TestStatusLogDeleteAPIView(StatusLogTestCase):
    """StatusLogViewSetのテストクラス (DELETE)"""

    def test_delete_success(self):
        """DELETEリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        state = StatusLogFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 204)
        self.assertEqual(StatusLog.objects.count(), 0)

    def test_delete_failure_invalid_user(self):
        """DELETEリクエスト (異常系: 他ユーザーのデータ削除不可)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user2)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        state = StatusLogFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)
        self.assertEqual(StatusLog.objects.count(), 1)

    def test_delete_failure_no_auth(self):
        """DELETEリクエスト (異常系: 認証なし)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        state = StatusLogFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)
        self.assertEqual(StatusLog.objects.count(), 1)
