from django.utils.timezone import now, timedelta

from backend.models import Book, Note, Note, Author, BookAuthorRelation
from apiv1.tests.testing import *
from apiv1.tests.factories import BookFactory, NoteFactory, create_dummy_notes


class NoteViewSetTestCase(UserAPITestCase):
    """雛形: NoteViewsetのテストクラス"""

    TARGET_URL = '/api/v1/note/'
    TARGET_URL_WITH_PK = '/api/v1/note/{}/'


class TestNoteCreateAPIView(NoteViewSetTestCase):
    """NoteViewSetのテストクラス (POST)"""

    def test_create_success(self):
        """POSTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        params = {**self.NOTE_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, 201)

        note = Note.objects.get()
        expected_json = get_expected_note_json(params, note)
        self.assertJSONEqual(response.content, expected_json)

    def test_create_failure_invalid_user(self):
        """登録APIへのPOSTリクエスト (異常系: バリデーションNG)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user2)
        params = {**self.NOTE_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Note.objects.count(), 0)

    def test_create_failure_no_auth(self):
        """登録APIへのPOSTリクエスト (異常系: 認証なし)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        params = {**self.NOTE_FIXTURE, 'book': book.id}

        """Act"""
        response = self.client.post(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)
        self.assertEqual(Note.objects.count(), 0)


class TestNoteUpdateAPIView(NoteViewSetTestCase):
    """NoteViewSetのテストクラス (PUT/PATCH)"""

    def test_put_success(self):
        """PUTリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        note = NoteFactory(book=book, created_by=self.user)
        params = {**self.STATUS_FIXTURE, 'id': note.id, 'book': book.id, 'content': 'foo bar'}

        """Act"""
        response = self.client.put(self.TARGET_URL_WITH_PK.format(note.id), params, format='json')

        """Assert"""
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        note = Note.objects.get()
        expected_json = get_expected_note_json(params, note)
        self.assertJSONEqual(response.content, expected_json)

    def test_patch_success(self):
        """PATCHリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        note = NoteFactory(book=book, created_by=self.user)
        params = {'content': 'foo bar'}

        """Act"""
        response = self.client.patch(self.TARGET_URL_WITH_PK.format(note.id), params, format='json')

        """Assert"""
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(response.status_code, 200)

        note = Note.objects.get()
        expected_json = get_expected_note_json(params, note)
        self.assertJSONEqual(response.content, expected_json)


class TestNoteRetrieveAPIView(NoteViewSetTestCase):
    """NoteViewSetのテストクラス (Retrieve)"""

    def test_retrieve_success(self):
        """GETリクエスト [Retrieve] (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        note = NoteFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(note.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        expected_json = get_expected_note_json({}, note)
        self.assertJSONEqual(response.content, expected_json)

    def test_retrieve_failure_invalid_user(self):
        """GETリクエスト [Retrieve] (異常系: 異なるユーザーによる権限エラー)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user2)
        note = NoteFactory(book=book, created_by=self.user2)

        """Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(note.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 404)

    def test_retrieve_failure_no_auth(self):
        """GETリクエスト [Retrieve] (異常系: 認証なし)"""

        """Arrange"""
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        note = NoteFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.get(self.TARGET_URL_WITH_PK.format(note.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 401)


class TestNoteListAPIView(NoteViewSetTestCase):
    """NoteViewSetのテストクラス (List)"""

    def test_list_success(self):
        """GETリクエスト [List] (正常系: 作成日時で降順ソート)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        notes = create_dummy_notes({**self.NOTE_FIXTURE, 'created_by': self.user}, 10)

        """Act"""
        response = self.client.get(self.TARGET_URL, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), len(notes))

        for i in range(10):
            result_id, note_id = results[i]['id'], str(notes[i].id)
            self.assertEqual(result_id, note_id)

    def test_list_success_pagination(self):
        """GETリクエスト [List] (正常系: ページネーション)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        notes = create_dummy_notes({**self.NOTE_FIXTURE, 'created_by': self.user}, 13)
        params = {'page': 2}

        """Act"""
        response = self.client.get(self.TARGET_URL, params, format='json')

        """Assert"""
        self.assertEqual(response.status_code, 200)
        results = response.data['results']
        self.assertEqual(len(results), 1)

        result_id, note_id = results[0]['id'], str(notes[-1].id)
        self.assertEqual(result_id, note_id)


class TestNoteDeleteAPIView(NoteViewSetTestCase):
    """NoteViewSetのテストクラス (DELETE)"""

    def test_delete_success(self):
        """DELETEリクエスト (正常系)"""

        """Arrange"""
        self.client.force_authenticate(user=self.user)
        book = BookFactory(**self.BOOK_FIXTURE, created_by=self.user)
        note = NoteFactory(book=book, created_by=self.user)

        """Act"""
        response = self.client.delete(self.TARGET_URL_WITH_PK.format(note.id), format='json')

        """Assert"""
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Note.objects.count(), 0)
