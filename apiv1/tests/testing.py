from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import random
import string
from django.utils.timezone import localtime

from backend.models import Book, Note, StatusLog

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

        self.BOOK_FIXTURE = {
            'title': 'test',
            'format_type': 0,
            'total': 100,
            'id_google': 'xxxxxxxxxx'
        }
        self.STATUS_FIXTURE = {
            'position': 10
        }


def convert_time_into_json_str(time):
    """timeをJSON形式に変換"""

    return str(localtime(time)).replace(' ', 'T')


def get_rand_id(n=12):
    """ランダムなID文字列を生成"""

    randlist = [random.choice(string.ascii_letters + string.digits) for _ in range(n)]
    return ''.join(randlist)


def get_expected_book_json(params, book: Book):
    """Assert対象のJSON書籍データを生成"""

    expected_json = {
        'id': str(book.id),
        'status': [],
        'note': [],
        'title': params.get('title') or book.title,
        'authors': [_ for _ in book.get_author_names()],
        'id_google': params.get('id_google') or book.id_google,
        'thumbnail': params.get('thumbnail') or book.thumbnail or DUMMY_THUMBNAIL_URL,
        'format_type': params.get('format_type') or book.format_type,
        'total': params.get('total') or book.total,
        'total_page': params.get('total_page') or book.total_page,
        'amazon_dp': params.get('amazon_dp') or book.amazon_dp,
        'created_at': convert_time_into_json_str(book.created_at),
    }

    return expected_json


def get_expected_state_json(params, state: StatusLog):
    """
    Assert対象のJSON進捗データを生成
    (書籍はformat_type=0、記録は初回分のデータにのみ有効)
    """

    if state.position == 0:
        state_name = 'to_be_read'
    elif state.position < state.book.total:
        state_name = 'reading'
    else:
        state_name = 'read'

    book_json = get_expected_book_json({}, state.book)
    del book_json['note'], book_json['status']
    position = params.get('position') or state.position

    expected_json = {
        'id': str(state.id),
        'state': state_name,
        'diff': {
            'value': position,
            'percentage': int(position / state.book.total * 100),
            'page': position
        },
        'position': {
            'value': position,
            'percentage': int(position / state.book.total * 100),
            'page': position
        },
        'created_at': convert_time_into_json_str(state.created_at),
        'book': book_json
    }

    return expected_json
