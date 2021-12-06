import uuid
from django.core.validators import MinLengthValidator

from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """ユーザーモデル"""

    class Meta:
        # db_table = 'user'
        verbose_name_plural = 'ユーザー'
        ordering = ['username']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField('写真', blank=True, null=True, default=None)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class BookOrigin(models.Model):

    class Meta:
        db_table = 'book_origin'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField('タイトル', max_length=100)
    authors = models.CharField('著者', max_length=100)
    thumbnail = models.URLField('書影URL', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class StatusLogManager(models.Manager):
    def filter_current_status(self, queryset, status=None):
        # BookCopyに対してstatus_logの最初のレコードでフィルタリング
        books_copy = queryset.prefetch_related('status_log')

        query = Q(id=None)

        for book_copy in books_copy:
            status_log = book_copy.status_log
            if not status_log.exists():
                if status == 'to_be_read':
                    query |= Q(id=book_copy.id)

                # reading or readを指定した場合→status_logが存在しないならqueryは追加しない
                continue

            position = status_log.first().position
            total = book_copy.total

            if position > 0:
                if status == 'reading' and position < total:
                    query |= Q(id=book_copy.id)
                elif status == 'read' and position >= total:
                    query |= Q(id=book_copy.id)

            elif status == 'to_be_read':
                query |= Q(id=book_copy.id)

        return books_copy.filter(query)


class BookCopy(models.Model):

    class Meta:
        db_table = 'book_copy'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book_origin = models.ForeignKey(BookOrigin, verbose_name='元データ', on_delete=models.CASCADE,
                                    related_name='books_copy')
    format_type = models.IntegerField(default=0, choices=((0, 'normal'), (1, 'ebook')))
    total = models.IntegerField(default=0)
    amazon_dp = models.CharField(max_length=13, validators=[MinLengthValidator(10)], null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, verbose_name='登録したユーザー',
                                   on_delete=models.SET_NULL, null=True, related_name='books_copy')
    objects = StatusLogManager()

    def __str__(self):
        return '{}->{}'.format(self.book_origin.title, self.created_by)


class Note(models.Model):

    class Meta:
        db_table = 'note'
        ordering = ['-created_at']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(BookCopy, verbose_name='書籍', on_delete=models.CASCADE,
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
    book = models.ForeignKey(BookCopy, verbose_name='書籍', on_delete=models.CASCADE,
                             related_name='status_log')
    position = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(CustomUser, verbose_name='登録したユーザー',
                                   on_delete=models.SET_NULL, null=True, related_name='status_log')
