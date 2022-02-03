from django_filters import rest_framework as django_filter
from apiv1.tests.mixins import UserAPITestCase

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation


class TestBookFilter(UserAPITestCase):
    """書籍検索フィルタのテストクラス"""

    # test_filter_title
    # test_filter_authors
    # test_filter_status
    # test_filter_accessed_at
    # test_filter_created_at
    # test_filter_q

    # test_filter_q_or
