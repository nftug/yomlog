from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import random
import string
from typing import OrderedDict
from django.db.models.query import QuerySet
from django.utils.timezone import localtime, now, timedelta

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation

DUMMY_THUMBNAIL_URL = 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=No+Image'


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

    def setUp(self):
        """setUpメソッド"""

        super().setUp()

        self.maxDiff = 1000

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
            'total': 2000,
            'total_page': 100
        }
        self.STATUS_FIXTURE = {
            'position': 10
        }

    def assertEqual_result_with_book(self, result: OrderedDict, book: Book):
        """
        出力結果と書籍レコードの内容を比較
        (プロパティの型変換も行う)
        """

        # 結果をOrderedDictから普通の辞書に変換
        result_dict = dict(result)
        # AuthorをQuerySetからstr型のlistに変換する
        authors: QuerySet = result_dict['authors']
        result_dict['authors'] = list(authors.values_list('author__name', flat=True))

        expected_json = get_expected_book_json({}, book)
        self.assertEqual(result_dict, expected_json)


def get_rand_id(n=12):
    """ランダムなID文字列を生成"""

    randlist = [random.choice(string.ascii_letters + string.digits) for _ in range(n)]
    return ''.join(randlist)


def create_dummy_book(params, user):
    """書籍のダミーデータを作成"""

    dummy_book_params = {**params}
    del dummy_book_params['authors']
    book = Book.objects.create(**dummy_book_params, created_by=user)

    for (i, author_name) in enumerate(params['authors']):
        author = Author.objects.create(name=author_name)
        BookAuthorRelation.objects.create(order=i, book=book, author=author)

    return book


def create_dummy_books(n, user, params):
    """n冊分のダミーデータを作成"""

    books = []
    for i in range(n):
        params = {
            **params,
            'id_google': get_rand_id(10),
            'created_at': now() + timedelta(seconds=i)
        }
        book = create_dummy_book(params=params, user=user)
        books.insert(0, book)

    return books


def get_expected_book_json(params, book: Book):
    """Assert対象のJSON書籍データを生成"""

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
        'thumbnail': params.get('thumbnail') or book.thumbnail or DUMMY_THUMBNAIL_URL,
        'format_type': params.get('format_type') or book.format_type,
        'total': params.get('total') or book.total,
        'total_page': params.get('total_page') or book.total_page,
        'amazon_dp': params.get('amazon_dp') or book.amazon_dp,
        'created_at': str(localtime(book.created_at)).replace(' ', 'T')
    }

    return expected_json


def create_dummy_state_and_book(params_state, params_book, user):
    """ダミーの進捗を作成"""

    book = create_dummy_book(params_book, user)
    params = {**params_state, 'book': book}
    state = StatusLog.objects.create(**params, created_by=user)
    return state, book


def create_dummy_status(params_state, params_book, n, user):
    """ダミーの進捗をn個作成"""

    status = []
    for i in range(n):
        params = {
            **params_state,
            'created_at': now() + timedelta(seconds=i)
        }
        state, book = create_dummy_state_and_book(params_state=params, params_book=params_book, user=user)
        status.insert(0, state)

    return status, book


def get_expected_status_json(params, status: StatusLog):
    """
    Assert対象のJSON進捗データを生成
    (書籍はformat_type=0、記録は初回分のデータにのみ有効)
    """

    if status.position == 0:
        state = 'to_be_read'
    elif status.position < status.book.total:
        state = 'reading'
    else:
        state = 'read'

    book_json = get_expected_book_json({}, status.book)
    del book_json['note'], book_json['status']
    position = params.get('position') or status.position

    expected_json = {
        'id': str(status.id),
        'state': state,
        'diff': {
            'value': position,
            'percentage': int(position / status.book.total * 100),
            'page': position
        },
        'position': {
            'value': position,
            'percentage': int(position / status.book.total * 100),
            'page': position
        },
        'created_at': str(localtime(status.created_at)).replace(' ', 'T'),
        'book': book_json
    }

    return expected_json
