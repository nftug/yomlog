import uuid
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.db.models import Max, F, Count
from django.db.models.functions import Coalesce
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """ユーザーモデル"""

    class Meta:
        db_table = 'user'
        verbose_name = 'ユーザー'
        verbose_name_plural = 'User'
        ordering = ['username']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, blank=True)
    avatar = models.ImageField('写真', blank=True, null=True, default=None)

    # EMAIL_FIELD = 'email'
    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['username']


class BookQuerySet(models.QuerySet):
    def filter_by_state(self, state):
        if not state:
            return self

        queryset = self.prefetch_related('status_log').distinct()
        ids = []

        if state == 'all':
            return queryset

        for book in queryset:
            status_log = book.status_log
            position = status_log.first().position if status_log.exists() else 0

            if position <= 0:
                if state == 'to_be_read':
                    ids.append(book.id)
                else:
                    continue
            else:
                if state == 'reading' and position < book.total:
                    ids.append(book.id)
                elif state == 'read' and position >= book.total:
                    ids.append(book.id)

        return queryset.filter(id__in=ids)

    def annotate_accessed_at(self):
        return self.annotate(accessed_at=Coalesce(Max('status_log__created_at'), F('created_at')))

    def sort_by_accessed_at(self):
        return self.annotate_accessed_at().order_by('-accessed_at')


class AuthorQuerySet(models.QuerySet):
    def sort_by_books_count(self):
        return self.annotate(Count('books')).order_by('-books__count')


class Author(models.Model):

    class Meta:
        db_table = 'author'
        ordering = ['-name']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    objects = AuthorQuerySet.as_manager()

    def __str__(self):
        return self.name


class Book(models.Model):

    class Meta:
        db_table = 'book'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_google = models.CharField(max_length=12)
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author, related_name='books', through='BookAuthorRelation')
    thumbnail = models.URLField(null=True, blank=True)
    format_type = models.IntegerField(default=0, choices=((0, 'normal'), (1, 'ebook')))
    total = models.IntegerField(default=0)
    total_page = models.IntegerField(default=0, null=True, blank=True)
    amazon_dp = models.CharField(max_length=13, validators=[MinLengthValidator(10)], null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='books')
    objects = BookQuerySet.as_manager()

    def __str__(self):
        return '{}: {}'.format(self.created_by, self.title)

    def get_author_names(self):
        # orderに合わせて著者名を並び替え
        through = self.authors.through
        return through.objects.filter(book=self).values_list('author__name', flat=True).order_by('order')


class BookAuthorRelation(models.Model):

    class Meta:
        db_table = 'book_author'
        ordering = ['book', 'order']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    order = models.IntegerField()


class Note(models.Model):

    class Meta:
        db_table = 'note'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='notes')
    position = models.IntegerField()
    quote_text = models.TextField(null=True, blank=True)
    quote_image = models.ImageField(blank=True, null=True, default=None)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='notes')


class StatusLog(models.Model):

    class Meta:
        db_table = 'status_log'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='status_log')
    position = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='status_log')
