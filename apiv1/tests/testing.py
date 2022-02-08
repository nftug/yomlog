from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
import random
import string
from django.utils.timezone import localtime
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from contextlib import contextmanager
import os

from apiv1.serializers import BookSerializer, StatusLogSerializer

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
            'position': 1
        }
        self.NOTE_FIXTURE = {
            'position': 1,
            'content': 'test\nテスト',
            'quote_text': 'ほげほげ'
        }

    def assert_book_included_dict(self, data, expected_dict, book):
        """bookの項目を含む辞書のアサーション"""

        for (key, value) in expected_dict.items():
            value = data[key]
            self.assertEqual(data[key], value)

        # 書籍情報の照合

        expected_book_json = get_expected_book_json({}, book, inside=True)
        for (key, value) in expected_book_json.items():
            book_value = data['book'][key]
            if isinstance(book_value, QuerySet):
                book_value = [_ for _ in book_value.values_list('author__name', flat=True).order_by('order')]
            self.assertEqual(book_value, value)


class UserSerializerTestCase(UserAPITestCase):
    def serializer_invalid(self, serializer, params, field, error, context=None):
        """雛形: 入力データのバリデーション (異常系: 必須フィールドが不正)"""

        """Arrange"""
        input_data = {**params}

        """Act"""
        serializer = serializer(data=input_data, context=context)

        """Assert"""
        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), [field])
        self.assertCountEqual(
            [str(x) for x in serializer.errors[field]],
            [error]
        )


def convert_time_into_json_str(time):
    """timeをJSON形式に変換"""

    return str(localtime(time)).replace(' ', 'T')


def get_rand_id(n=12):
    """ランダムなID文字列を生成"""

    randlist = [random.choice(string.ascii_letters + string.digits) for _ in range(n)]
    return ''.join(randlist)


def get_expected_book_json(params, book: Book, inside=False):
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

    if inside:
        del expected_json['status'], expected_json['note']

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

    book_json = get_expected_book_json({}, state.book, inside=True)
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


def get_expected_note_json(params, note: Note):
    """ Assert対象のJSONノートデータを生成"""

    book_json = get_expected_book_json({}, note.book, inside=True)
    quote_image_origin = str(note.quote_image) if note.quote_image else None

    expected_json = {
        'id': str(note.id),
        'position': params.get('position') or note.position,
        'quote_text': params.get('quote_text') or note.quote_text,
        'quote_image': params.get('quote_image') or quote_image_origin,
        'content': params.get('content') or note.content,
        'created_at': convert_time_into_json_str(note.created_at),
        'book': book_json
    }

    return expected_json


@contextmanager
def create_dummy_jpeg(filename='test_image.jpg'):
    """ダミー画像 (JPEG) を生成して返す"""

    try:
        image = BytesIO()
        Image.new('RGB', (100, 100)).save(image, 'JPEG')
        image.seek(0)
        image_file = SimpleUploadedFile(name=filename, content=image.getvalue(), content_type='image/jpeg')
        yield image_file
    finally:
        filename = os.path.join(settings.MEDIA_ROOT, image_file.name)
        if os.path.exists(filename):
            os.remove(filename)