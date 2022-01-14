from rest_framework import serializers
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError
from django.conf import settings

from .mixins import ImageSerializerMixin
from backend.models import Author, Book, StatusLog, Note, BookAuthorRelation

from datetime import date, timedelta, datetime

import math
import re


class PostSerializer(serializers.ModelSerializer, ImageSerializerMixin):
    def get_created_by(self, instance):
        from auth.serializers import CustomUserListSerializer
        return CustomUserListSerializer(instance.created_by, many=False, read_only=True).data

    def create(self, validated_data):
        user = super().context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)


class BookIncludedSerializer(PostSerializer):
    def get_book(self, instance):
        return BookSerializer(instance.book, context={'inside': True}).data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not super().context.get('inside'):
            ret['book'] = self.get_book(instance)

        return ret

    def validate_book(self, data):
        if data.created_by != super().context['request'].user:
            raise ValidationError('自ユーザーが作成した本を選択してください')

        return data


class StatusLogSerializer(BookIncludedSerializer):
    # created_by = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    diff = serializers.SerializerMethodField()

    class Meta:
        model = StatusLog
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'allow_null': True},
            'book': {'write_only': True}
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['position'] = self.get_position(instance)

        return ret

    def get_state(self, instance):
        if instance.position == 0:
            return 'to_be_read'
        elif instance.position < instance.book.total:
            return 'reading'
        else:
            return 'read'

    @classmethod
    def get_diff(self, instance):
        # 前回までに進んだページ数 or 位置No
        book = instance.book
        base_status = instance

        while True:
            prev_status = StatusLog.objects.filter(
                book=book, created_at__lt=base_status.created_at
            ).order_by('-created_at').first()

            if not prev_status or prev_status.position > 0:
                break

            base_status = prev_status

        if prev_status and instance.position > prev_status.position:
            diff = instance.position - prev_status.position
        elif not prev_status:
            diff = instance.position
        else:
            diff = 0

        percentage = diff / instance.book.total
        page = math.ceil(book.total_page * percentage) if book.format_type == 1 else diff

        return {
            'value': diff,
            'percentage': int(percentage * 100),
            'page': page
        }

    def get_position(self, instance):
        book = instance.book
        position = instance.position

        if instance.position == 0:
            # 積読中の場合、進捗の位置はその本の直前のステータスを参照する
            prev_status = StatusLog.objects.filter(
                book=instance.book, created_at__lt=instance.created_at
            ).order_by('-created_at').first()

            if prev_status:
                position = prev_status.position

        percentage = position / book.total
        page = math.ceil(book.total_page * percentage) if book.format_type == 1 else position

        return {
            'value': position,
            'percentage': int(percentage * 100),
            'page': page
        }


class NoteSerializer(BookIncludedSerializer):
    class Meta:
        model = Note
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
            'quote_text': {'required': False},
            'quote_image': {'required': False},
            'book': {'write_only': True}
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        quote_image = ret['quote_image']
        if quote_image and quote_image.startswith('/'):
            ret['quote_image'] = '{}{}'.format(settings.HOST_URL, quote_image)
        return ret


class BookSerializer(PostSerializer):
    # created_by = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()
    authors = serializers.ListField(
        child=serializers.CharField(max_length=100), write_only=True
    )

    class Meta:
        model = Book
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
            'total_page': {'required': False, 'allow_null': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['authors'] = instance.get_author_names()
        ret['thumbnail'] = self.get_thumbnail(instance)

        if self.context.get('inside'):
            del ret['status'], ret['note']
        return ret

    def _get_or_create_authors(self, validated_data):
        authors = []

        # 関連先のAuthorオブジェクトを登録
        for name in validated_data['authors']:
            author, created = Author.objects.get_or_create(name=name)
            authors.append(author)

        return authors

    def create(self, validated_data):
        authors = self._get_or_create_authors(validated_data)

        # 登録したAuthorオブジェクトをbookに紐付けする
        del validated_data['authors']
        book = super().create(validated_data)

        for i, author in enumerate(authors):
            BookAuthorRelation.objects.create(order=i, book=book, author=author)

        return book

    def update(self, instance, validated_data):
        authors = self._get_or_create_authors(validated_data)

        del validated_data['authors']
        book = super().update(instance, validated_data)

        # 事前に中間テーブルを削除しておく
        BookAuthorRelation.objects.filter(book=book).delete()

        for i, author in enumerate(authors):
            BookAuthorRelation.objects.create(order=i, book=book, author=author)

        # orphanedなAuthorオブジェクトを削除
        Author.objects.filter(books=None).delete()

        return book

    def validate_authors(self, values):
        """著者名の正規化"""

        authors = []
        for value in values:
            value = re.sub(r'([^0-9a-z]) |　', r'\1', value)
            authors.append(value)

        return authors

    def get_status(self, instance):
        if not self.context.get('inside'):
            status_log = instance.status_log.select_related('book').order_by('-created_at')
            data = StatusLogSerializer(status_log, many=True, read_only=True, context={'inside': True}).data
            return data
        else:
            return None

    def get_note(self, instance):
        if not self.context.get('inside'):
            notes = instance.notes.select_related('book').order_by('position')
            return NoteSerializer(notes, many=True, read_only=True, context={'inside': True}).data
        else:
            return None

    def get_thumbnail(self, instance):
        NO_COVER_IMAGE = 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=No+Image'
        return instance.thumbnail or NO_COVER_IMAGE


class AnalyticsSerializerMixin():
    """分析用シリアライザ ミックスイン"""

    def _get_diff_total(self, status_log: StatusLog):
        """進捗の累計ページ数を取得"""

        total = 0
        for status in status_log:
            total += StatusLogSerializer.get_diff(status)['page']

        return total


class AnalyticsSerializer(serializers.Serializer, AnalyticsSerializerMixin):
    """分析用シリアライザ"""

    number_of_books = serializers.SerializerMethodField()
    pages_read = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()

    def get_number_of_books(self, status_log: StatusLog):
        """ステータスごとの累計冊数を取得"""

        # status_logに関連づけられたbooksをまとめて取得
        status_ids = set(status_log.values_list('id', flat=True))
        books = Book.objects.filter(status_log__id__in=status_ids)

        return {
            'to_be_read': Book.objects.filter_by_state('to_be_read').count(),
            'reading': books.filter_by_state('reading').count(),
            'read': books.filter_by_state('read').count()
        }

    def get_pages_read(self, status_log: StatusLog):
        """読書ページ数の累計と、一日毎の平均ページ数を取得"""

        # NOTE: total_pageの情報を持たないKindle本はカウントしない
        # TODO: Kindleの位置Noとページ数に固定の相関性はあるか？あとで調べる。

        # 全体の累計ページ数を取得
        total = self._get_diff_total(status_log)

        # 平均ページ数の計算は、フィルタで指定された日付範囲に依拠させる
        if self.context.get('filterset'):
            created_at = self.context['filterset'].form.cleaned_data.get('created_at')
            start_date = created_at.start.date() if hasattr(created_at, 'start') \
                else status_log.last().created_at.date()
            end_date = created_at.end.date() if hasattr(created_at, 'end') \
                else date.today()
        else:
            # ユーザー情報から呼び出された場合、start_dateはユーザーの登録日
            start_date = self.context['request'].user.date_joined.date()
            end_date = date.today()
            status_log = status_log.filter(created_at__date__gte=start_date)

        total_for_avg = self._get_diff_total(status_log)
        days_for_avg = (end_date - start_date).days + 1

        return {
            'total': total,
            'avg_per_day': int(total_for_avg / (days_for_avg or 1)),
        }

    def get_days(self, status_log: StatusLog):
        """トータルの読書日数、連続読書日数を取得"""

        # 記録された日数のset
        date_set = set(status_log.values_list('created_at__date', flat=True))
        sorted_date_set = sorted(list(date_set))
        cur_date = None

        # 連続読書日数のカウントを開始
        for i, cur_date in enumerate(sorted_date_set):
            if i == 0:
                continuous = 1
                continue

            if cur_date - timedelta(days=1) == sorted_date_set[i - 1]:
                # 直前の記録と連続
                continuous += 1
            else:
                # 直前の記録から途切れた
                continuous = 1

        # 記録がないか、直前の記録の日付の差から2日以上空いている場合、continuousを0にする
        if cur_date is None or (date.today() - cur_date).days > 1:
            continuous = 0

        return {
            'total': len(date_set),
            'continuous': continuous
        }


class AuthorSerializer(serializers.ModelSerializer):
    """著者名リスト用シリアライザ"""

    count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['name', 'count']

    def get_count(self, instance: Author):
        return instance.books__count


class PagesDailySerializer(serializers.Serializer, AnalyticsSerializerMixin):
    """
    ページ数集計用シリアライザ
    (instanceにはdate_createdがmany=Trueで入る。コンテキストからquerysetを取得。)
    """

    date = serializers.SerializerMethodField()
    pages = serializers.SerializerMethodField()

    def get_date(self, date_created):
        return date_created

    def get_pages(self, date_created):
        """一日毎のページ数集計を取得"""
        queryset = self.context['queryset']
        status_daily = queryset.filter(created_at__date=date_created)
        pages_daily = self._get_diff_total(status_daily) if status_daily.exists() else 0
        return pages_daily
