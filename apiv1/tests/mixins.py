from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
import random
import string


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

    def _get_rand_id(self, n=12):
        """ランダムなID文字列を生成"""

        randlist = [random.choice(string.ascii_letters + string.digits) for _ in range(n)]
        return ''.join(randlist)
