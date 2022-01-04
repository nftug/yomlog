from typing import OrderedDict
from rest_framework import serializers
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError
from django.conf import settings

from .mixins import ImageSerializerMixin
from backend.models import Book, StatusLog, Note

from datetime import datetime
from datetime import timedelta
from django.db.models import Q, Count
import math


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

    class Meta:
        model = Book
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['authors'] = self.get_authors(instance)
        if self.context.get('inside'):
            del ret['status'], ret['note']
        return ret

    def get_status(self, instance):
        if not self.context.get('inside'):
            status_log = instance.status_log.order_by('-created_at')
            data = StatusLogSerializer(status_log, many=True, read_only=True, context={'inside': True}).data
            return data
        else:
            return None

    def get_authors(self, instance):
        return instance.authors.split(',')

    def get_note(self, instance):
        if not self.context.get('inside'):
            notes = instance.notes.order_by('position')
            return NoteSerializer(notes, many=True, read_only=True, context={'inside': True}).data
        else:
            return None


class AnalyticsSerializer(serializers.Serializer):
    number_of_books = serializers.SerializerMethodField()
    pages_read = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()

    def _get_period_days(self, status_data: OrderedDict):
        # StatusLogの最初と最後の日数差を取得
        if status_data:
            newest_td, oldest_td = [status_data[0]['created_at'], status_data[-1]['created_at']]
            diff_td = datetime.fromisoformat(newest_td.split('T')[0]) - datetime.fromisoformat(oldest_td.split('T')[0])
            return diff_td.days + 1
        else:
            return 1

    def get_number_of_books(self, status_log: StatusLog):
        # status_logに関連づけられたbooksをまとめて取得
        query = Q(id=None)
        for status in status_log:
            query |= Q(id=status.book.id)
        books = Book.objects.filter(query)

        return {
            'to_be_read': books.filter_by_state('to_be_read').count(),
            'reading': books.filter_by_state('reading').count(),
            'read': books.filter_by_state('read').count()
        }

    def get_pages_read(self, status_log: StatusLog):
        # NOTE: total_pageの情報を持たない本はカウントしない
        # TODO: Kindleの位置Noとページ数に固定の相関性はあるか？あとで調べる。

        status_data = StatusLogSerializer(status_log, many=True, read_only=True, context={'inside': True}).data
        total = 0
        for status in status_data:
            total += status['diff']['page']

        period_days = self._get_period_days(status_data)

        return {
            'total': total,
            'avg_per_day': int(total / period_days)
        }

    def get_days(self, status_log: StatusLog):
        # トータルの記録日数と連速記録日数を取得

        # 記録された日数のset
        date_set = set(status_log.values_list('created_at__date', flat=True))

        sorted_date_set = sorted(list(date_set))
        continuous = 0

        for i, cur_date in enumerate(sorted_date_set):
            if i == 0:
                continuous = 0
                continue

            if cur_date - timedelta(days=1) == sorted_date_set[i - 1]:
                # 連続
                continuous += 1
            else:
                # 途切れた
                break

        return {
            'total': len(date_set),
            'continuous': continuous
        }
