from typing import OrderedDict
from rest_framework import serializers
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError
from django.conf import settings

from .mixins import ImageSerializerMixin
from backend.models import Author, Book, StatusLog, Note

from datetime import datetime, date
from datetime import timedelta
from django.db.models import Q, Count
import math
from itertools import islice


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
    authors = serializers.CharField(max_length=200)

    class Meta:
        model = Book
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['authors'] = [_.name for _ in instance.authors.all()]

        if self.context.get('inside'):
            del ret['status'], ret['note']
        return ret

    def _get_or_create_authors(self, validated_data):
        authors = []

        # 関連先のAuthorオブジェクトを登録 (カンマ区切り)
        for name in validated_data['authors'].split(','):
            author, created = Author.objects.get_or_create(name=name)
            authors.append(author)

        del validated_data['authors']
        return authors

    def create(self, validated_data):
        authors = self._get_or_create_authors(validated_data)

        # 登録したAuthorオブジェクトをbookに紐付けする
        book = super().create(validated_data)
        book.authors.set(authors)
        return book

    def update(self, instance, validated_data):
        authors = self._get_or_create_authors(validated_data)

        book = super().update(instance, validated_data)
        book.authors.set(authors)

        # orphanedなAuthorオブジェクトを削除
        queryset = Author.objects.filter(books=None)
        queryset.delete()

        return book

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


class AnalyticsSerializer(serializers.Serializer):
    """分析用シリアライザ"""

    number_of_books = serializers.SerializerMethodField()
    pages_read = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()
    authors_count = serializers.SerializerMethodField()

    def _get_period_days(self, status_log: StatusLog):
        """ユーザー登録日 or 記録の開始日から今日までの日数を計算"""

        user = self.context['request'].user
        date_joined = user.date_joined.date()

        prev_status_log = status_log.filter(created_at__lt=date_joined)
        if prev_status_log.exists():
            diff_td = date.today() - prev_status_log.first().created_at.date()
        else:
            diff_td = date.today() - date_joined

        return diff_td.days

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

        # NOTE: total_pageの情報を持たない本はカウントしない
        # TODO: Kindleの位置Noとページ数に固定の相関性はあるか？あとで調べる。

        status_data = StatusLogSerializer(status_log, many=True, read_only=True, context={'inside': True}).data
        total = 0
        for status in status_data:
            total += status['diff']['page']

        period_days = self._get_period_days(status_log)

        return {
            'total': total,
            'avg_per_day': int(total / (period_days or 1)),
        }

    def get_days(self, status_log: StatusLog):
        """登録日からの経過日数、トータルの読書日数、連続読書日数を取得"""

        # 記録された日数のset (積読状態を除く)
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
                # print(cur_date, sorted_date_set[i - 1])
                continuous += 1
            else:
                # 直前の記録から途切れた
                # print('continuous = 1')
                continuous = 1

        # 記録がないか、直前の記録の日付の差から2日以上空いている場合、continuousを0にする
        if cur_date is None or (date.today() - cur_date).days > 1:
            continuous = 0

        return {
            'since_joined': self._get_period_days(status_log),
            'total': len(date_set),
            'continuous': continuous
        }

    def get_authors_count(self, status_log: StatusLog):
        """先頭<head>件 (default: 5) で著者名の集計を降順で取得"""

        user = self.context['request'].user
        authors = Author.objects.filter(books__created_by=user).annotate(Count('books'))

        # 著者名ごとに冊数を集計
        counts_of_authors = {}
        for author in authors:
            counts_of_authors[author.name] = author.books__count

        counts_of_authors = OrderedDict(
            sorted(counts_of_authors.items(), key=lambda x: x[1], reverse=True)
        )

        # headパラメータで切り出す数を指定し、カウントリストを降順で切り出す
        head = self.context['request'].GET.get('head')
        head = int(head) if head and head.isdecimal() else 5
        sliced_counts = OrderedDict(islice(counts_of_authors.items(), head))

        return sliced_counts
