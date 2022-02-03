from django.utils.timezone import now, timedelta

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.tests.mixins import UserAPITestCase


class StatusLogTestCase(UserAPITestCase):
    """雛形: StatusLogViewsetのテストクラス"""

    TARGET_URL = '/api/v1/status/'
    TARGET_URL_WITH_PK = '/api/v1/status/{}/'


class TestBookCreateAPIView(StatusLogTestCase):
    """StatusViewSetのテストクラス (POST)"""

    def test_create_success(self):
        """POSTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS, self.user)
        params = {**self.STATUS_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(StatusLog.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

        status = StatusLog.objects.get()
        expected_json = self._get_expected_status_json(params, status)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_failure_invalid_user(self):
        """登録APIへのPOSTリクエスト (異常系: バリデーションNG)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS, self.user2)
        params = {**self.STATUS_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 400)
        self.assertEqual(StatusLog.objects.count(), 0)

    def test_create_failure_no_auth(self):
        """登録APIへのPOSTリクエスト (異常系: 認証なし)"""

        """Arrange"""
        book = self._create_dummy_book(self.FIRST_BOOK_PARAMS, self.user)
        params = {**self.STATUS_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)
        self.assertEqual(StatusLog.objects.count(), 0)
