from datetime import datetime
from django.http import QueryDict
from django.utils.timezone import make_aware, timedelta, now
from datetime import datetime

from backend.models import Note
from apiv1.tests.testing import *
from apiv1.filters import NoteFilter
from apiv1.tests.factories import BookFactory, BookFactoryWithThreeAuthors, NoteFactory


class TestNoteFilter(UserAPITestCase):
    """ノート検索フィルタのテストクラス"""

    def test_filter_content(self):
        """メモ内容による絞り込み (正常系)"""

        # Arrange
        book = BookFactory(title='テスト用の本', created_by=self.user)
        input_data = {'book': book, 'position': 1, 'created_by': self.user, 'quote_text': 'テスト'}
        note_first = NoteFactory(**input_data, content='テスト')
        note_second = NoteFactory(**input_data, content='ほげほげ')
        qd = QueryDict('content=テス ト')

        # Act
        filterset = NoteFilter(qd, queryset=Note.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, note_first.id)

    def test_filter_quote_text(self):
        """引用内容による絞り込み (正常系)"""

        # Arrange
        book = BookFactory(title='テスト用の本', created_by=self.user)
        input_data = {'book': book, 'position': 1, 'created_by': self.user, 'content': 'テスト'}
        note_first = NoteFactory(**input_data, quote_text='テスト')
        note_second = NoteFactory(**input_data, quote_text='ほげほげ')
        qd = QueryDict('quote_text=テス ト')

        # Act
        filterset = NoteFilter(qd, queryset=Note.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, note_first.id)

    def test_filter_title(self):
        """書籍のタイトルによる絞り込み (正常系)"""

        # Arrange
        book_first = BookFactory(title='Test Book', created_by=self.user)
        book_second = BookFactory(title='テスト用の本', created_by=self.user)
        note_first = NoteFactory(**self.NOTE_FIXTURE, book=book_first, created_by=self.user)
        note_second = NoteFactory(**self.NOTE_FIXTURE, book=book_second, created_by=self.user)
        qd = QueryDict('title=test')

        # Act
        filterset = NoteFilter(qd, queryset=Note.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, note_first.id)

    def test_filter_authors(self):
        """書籍の著者名による絞り込み (正常系)"""

        # Arrange
        book_first = BookFactoryWithThreeAuthors(
            authors1__author__name='テスト次郎',
            authors2__author__name='Test Taro',
            authors3__author__name='Jane Doe',
            created_by=self.user
        )
        book_second = BookFactoryWithThreeAuthors(
            authors1__author__name='テスト太郎',
            authors2__author__name='Test Taro',
            authors3__author__name='Jane Doe',
            created_by=self.user
        )
        note_first = NoteFactory(**self.NOTE_FIXTURE, book=book_first, created_by=self.user)
        note_second = NoteFactory(**self.NOTE_FIXTURE, book=book_second, created_by=self.user)
        qd = QueryDict('authors=次郎')

        # Act
        filterset = NoteFilter(qd, queryset=Note.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, note_first.id)

    def test_filter_created_at(self):
        """ノートの作成日による範囲絞り込み (正常系)"""

        # Arrange
        note_first = NoteFactory(created_at=make_aware(datetime(2022, 1, 1)), created_by=self.user)
        note_second = NoteFactory(created_at=make_aware(datetime(2022, 1, 3)), created_by=self.user)
        qd = QueryDict('created_at_after=2022-01-01&created_at_before=2022-01-02')

        # Act
        filterset = NoteFilter(qd, queryset=Note.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, note_first.id)

    def test_filter_q(self):
        """フリーワードによる絞り込み (正常系)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        book_second = BookFactory(title='ほげほげ2', authors__author__name='テスト二郎', created_by=self.user)
        book_third = BookFactory(title='ほげほげ3', authors__author__name='テスト三郎', created_by=self.user)
        book_fourth = BookFactory(title='ほげほげ4', authors__author__name='テスト四郎', created_by=self.user)
        book_fifth = BookFactory(title='ほげほげ5', authors__author__name='テスト五郎', created_by=self.user)
        input_data = {'position': 1, 'created_by': self.user}
        note_first = NoteFactory(**input_data, book=book_first, quote_text='hoge')
        note_second = NoteFactory(**input_data, book=book_second, content='fuga')
        note_third = NoteFactory(**input_data, book=book_third, content='piyo', quote_text='foobar')
        note_fourth = NoteFactory(**input_data, book=book_fourth, content='test')
        note_fifth = NoteFactory(**input_data, book=book_fifth, content='test2')

        qd = QueryDict('q=一郎 OR fuga OR foobar OR ほげほげ4')

        # Act
        filterset = NoteFilter(qd, queryset=Note.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 4)
        self.assertNotEqual(queryset.filter(id=note_fifth.id).exists(), True)

    def test_filter_q_with_book(self):
        """フリーワードによる絞り込み (正常系: 書籍指定時の捜査対象変更)"""

        # Arrange
        book_first = BookFactory(title='ほげほげ1', authors__author__name='テスト一郎', created_by=self.user)
        input_data = {'position': 1, 'created_by': self.user}
        note_first = NoteFactory(**input_data, book=book_first, content='ほげテスト')
        note_second = NoteFactory(**input_data, book=book_first, content='fuga')

        qd = QueryDict(f'book={book_first.id}&q=ほげ OR テスト')

        # Act
        filterset = NoteFilter(qd, queryset=Note.objects.all())
        queryset = filterset.qs

        # Assert
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.filter(id=note_first.id).exists(), True)
