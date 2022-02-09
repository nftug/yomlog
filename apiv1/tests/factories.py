import factory
from django.utils.timezone import now, timedelta

from backend.models import Book, Note, StatusLog, Author, BookAuthorRelation, CustomUser
from apiv1.tests.testing import get_rand_id


class AuthorFactory(factory.django.DjangoModelFactory):
    name = 'author name'

    class Meta:
        model = Author


class BookBaseFactory(factory.django.DjangoModelFactory):
    title = 'test'
    format_type = 0
    total = 100
    id_google = 'xxxxxxxxxx'

    class Meta:
        model = Book


class BookAuthorRelationFactory(factory.django.DjangoModelFactory):
    book = factory.SubFactory(BookBaseFactory)
    author = factory.SubFactory(AuthorFactory)
    order = 0

    class Meta:
        model = BookAuthorRelation


class BookFactory(BookBaseFactory):
    authors = factory.RelatedFactory(BookAuthorRelationFactory, 'book')


class BookFactoryWithThreeAuthors(BookBaseFactory):
    authors1 = factory.RelatedFactory(BookAuthorRelationFactory, 'book', author__name='テスト太郎', order=0)
    authors2 = factory.RelatedFactory(BookAuthorRelationFactory, 'book', author__name='Test Taro', order=1)
    authors3 = factory.RelatedFactory(BookAuthorRelationFactory, 'book', author__name='Jane Doe', order=2)


def create_dummy_books(params_dict, n):
    books = []
    for i in range(n):
        params = {
            **params_dict,
            'id_google': get_rand_id(10),
            'created_at': now() + timedelta(seconds=i)
        }
        book = BookFactory(**params)
        books.insert(0, book)

    return books


class StatusLogFactory(factory.django.DjangoModelFactory):
    book = factory.SubFactory(BookFactory)
    position = 1

    class Meta:
        model = StatusLog


def create_dummy_status(params_dict, n):
    book = BookFactory(created_by=params_dict['created_by'])
    status = []
    for i in range(n):
        params = {
            **params_dict,
            'book': book,
            'position': i + 1,
            'created_at': now() + timedelta(seconds=i)
        }
        state = StatusLogFactory(**params)
        status.insert(0, state)

    return status


class NoteFactory(factory.django.DjangoModelFactory):
    book = factory.SubFactory(BookFactory)
    position = 10

    class Meta:
        model = Note


def create_dummy_notes(params_dict, n):
    book = BookFactory(created_by=params_dict['created_by'])
    notes = []
    for i in range(n):
        params = {
            **params_dict,
            'book': book,
            'position': i + 1,
            'created_at': now() + timedelta(seconds=i)
        }
        state = NoteFactory(**params)
        notes.insert(0, state)

    return notes


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser
