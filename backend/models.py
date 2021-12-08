import uuid
from django.core.validators import MinLengthValidator

from django.db import models
from django.utils import timezone
from django.db.models import Q, Max
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """ユーザーモデル"""

    class Meta:
        db_table = 'user'
        verbose_name_plural = 'ユーザー'
        ordering = ['username']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField('写真', blank=True, null=True, default=None)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class BookQuerySet(models.QuerySet):
    def filter_by_state(self, state):
        queryset = self.prefetch_related('status_log')
        query = Q(id=None)

        for book in queryset:
            status_log = book.status_log
            position = status_log.first().position if status_log.exists() else 0

            if position <= 0:
                if state == 'to_be_read':
                    query |= Q(id=book.id)
                else:
                    continue
            else:
                if state == 'reading' and position < book.total:
                    query |= Q(id=book.id)
                elif state == 'read' and position >= book.total:
                    query |= Q(id=book.id)

        return queryset.filter(query)

    def sort_by_state(self):
        return self.annotate(last_status_date=Max('status_log__created_at')).order_by('-last_status_date', '-created_at')


class Book(models.Model):

    class Meta:
        db_table = 'book'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_google = models.CharField('Google Books ID', max_length=12)
    title = models.CharField('タイトル', max_length=100)
    authors = models.CharField('著者', max_length=100)
    thumbnail = models.URLField('書影URL', null=True, blank=True)
    format_type = models.IntegerField(default=0, choices=((0, 'normal'), (1, 'ebook')))
    total = models.IntegerField(default=0)
    amazon_dp = models.CharField(max_length=13, validators=[MinLengthValidator(10)], null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, verbose_name='登録したユーザー',
                                   on_delete=models.SET_NULL, null=True, related_name='books')
    objects = BookQuerySet.as_manager()

    def __str__(self):
        return '{}: {}'.format(self.created_by, self.title)


class Note(models.Model):

    class Meta:
        db_table = 'note'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, verbose_name='書籍', on_delete=models.CASCADE,
                             related_name='notes')
    position = models.IntegerField()
    quote_text = models.TextField(null=True, blank=True)
    quote_image = models.ImageField(blank=True, null=True, default=None)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, verbose_name='登録したユーザー',
                                   on_delete=models.SET_NULL, null=True, related_name='notes')


class StatusLog(models.Model):

    class Meta:
        db_table = 'status_log'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, verbose_name='書籍', on_delete=models.CASCADE,
                             related_name='status_log')
    position = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, verbose_name='登録したユーザー',
                                   on_delete=models.SET_NULL, null=True, related_name='status_log')
