from django.utils.timezone import now, timedelta

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.tests.mixins import *


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
        book = create_dummy_book(self.FIRST_BOOK_PARAMS, self.user)
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
        book = create_dummy_book(self.FIRST_BOOK_PARAMS, self.user2)
        params = {**self.STATUS_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 400)
        self.assertEqual(StatusLog.objects.count(), 0)

    def test_create_failure_no_auth(self):
        """登録APIへのPOSTリクエスト (異常系: 認証なし)"""

        """Arrange"""
        book = create_dummy_book(self.FIRST_BOOK_PARAMS, self.user)
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
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user)

        """Act"""
        params = {**self.STATUS_FIXTURE, 'id': state.id, 'book': book.id, 'position': 100}
        response = self.client.put(self.TARGET_URL_WITH_PK.format(state.id), params, format='json')

        """Assert"""
        self.assertEqual(StatusLog.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        state = StatusLog.objects.get()
        expected_json = get_expected_state_json(params, state)
        self.assertJSONEqual(response.content, expected_json)

    def test_put_failure_validation(self):
        """PUTリクエスト (異常系: バリデーションNG)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user)

        """Act"""
        params = {**self.STATUS_FIXTURE, 'id': state.id, 'book': book.id, 'position': -1}
        response = self.client.put(self.TARGET_URL_WITH_PK.format(state.id), params, format='json')

        """Assert"""
        self.assertEqual(StatusLog.objects.count(), 1)
        self.assertEqual(response.status_code, 400)

    def test_put_failure_invalid_user(self):
        """PUTリクエスト (異常系: 異なるユーザーによる権限エラー)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user2)

        """Act"""
        params = {**self.STATUS_FIXTURE, 'id': state.id, 'book': book.id, 'position': 100}
        response = self.client.put(self.TARGET_URL_WITH_PK.format(state.id), params, format='json')

        """Assert"""
        self.assertEqual(StatusLog.objects.count(), 1)
        self.assertEqual(response.status_code, 404)

    def test_patch_success(self):
        """PATCHリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user)

        """Act"""
        params = {'position': 100}
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
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user)

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
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user2)

        """Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)

    def test_retrieve_failure_no_auth(self):
        """GETリクエスト [Retrieve] (異常系: 認証なし)"""

        """Arrange"""
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user2)

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
        status, book = create_dummy_status_and_book(
            params_state=self.STATUS_FIXTURE,
            params_book=self.FIRST_BOOK_PARAMS,
            n=10, user=self.user
        )

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
        status, book = create_dummy_status_and_book(
            params_state=self.STATUS_FIXTURE,
            params_book=self.FIRST_BOOK_PARAMS,
            n=13, user=self.user
        )
        params = {'page': 2}

        """Act"""
        response = self.client.get(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), 1)

        result_id, state_id = results[0]['id'], str(status[-1].id)
        self.assertEqual(result_id, state_id)

    def test_list_success_exclude_other_user(self):
        """GETリクエスト [List] (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user2)
        status, book = create_dummy_status_and_book(
            params_state=self.STATUS_FIXTURE,
            params_book=self.FIRST_BOOK_PARAMS,
            n=10, user=self.user
        )
        # 最後の一件のみ、レコードの作成者をuser2に設定する
        status[-1].created_by = self.user2
        status[-1].save()

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), 1)

        result_id, state_id = results[0]['id'], str(status[-1].id)
        self.assertEqual(result_id, state_id)

    def test_list_failure_no_auth(self):
        """GETリクエスト [List] (異常系: 認証なし)"""

        """Arrange"""
        status, book = create_dummy_status_and_book(
            params_state=self.STATUS_FIXTURE,
            params_book=self.FIRST_BOOK_PARAMS,
            n=10, user=self.user
        )

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)


class TestStatusLogDeleteAPIView(StatusLogTestCase):
    """StatusLogViewSetのテストクラス (DELETE)"""

    def test_delete_success(self):
        """DELETEリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user)

        """Act"""
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 204)
        self.assertEqual(StatusLog.objects.count(), 0)

    def test_delete_failure_invalid_user(self):
        """DELETEリクエスト (異常系: 他ユーザーのデータ削除不可)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user2)
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user)

        """Act"""
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)
        self.assertEqual(StatusLog.objects.count(), 1)

    def test_delete_failure_no_auth(self):
        """DELETEリクエスト (異常系: 認証なし)"""

        """Arrange"""
        state, book = create_dummy_state_and_book(self.STATUS_FIXTURE, self.FIRST_BOOK_PARAMS, self.user)

        """Act"""
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(state.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)
        self.assertEqual(StatusLog.objects.count(), 1)
