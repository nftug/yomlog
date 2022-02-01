from django.db.models.query import QuerySet
from django.utils.timezone import localtime, now, timedelta

from apiv1.tests.mixins import UserAPITestCase
from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation
from apiv1.serializers import BookSerializer


class TestBookPostSerializer(UserAPITestCase):
    """BookSerializerのテストクラス (投稿)"""

    def test_input_valid(self):
        """入力データのバリデーション (正常系)"""

        """Arrange"""
        input_data = self.FIRST_BOOK_PARAMS

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), True)

    # TODO: 正常系で著者欄が空欄の場合のテストを作成

    def test_input_invalid_if_title_blank(self):
        """入力データのバリデーション (異常系: タイトルが空文字)"""

        """Arrange"""
        input_data = {
            **self.FIRST_BOOK_PARAMS,
            'title': ''
        }

        """Act"""
        serializer = BookSerializer(data=input_data)

        """Assert"""
        self.assertEqual(serializer.is_valid(), False)
        self.assertCountEqual(serializer.errors.keys(), ['title'])
        self.assertCountEqual(
            [str(x) for x in serializer.errors['title']],
            ['この項目は空にできません。']
        )
