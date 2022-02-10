from pkg_resources import ensure_directory
from rest_framework import serializers
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.utils.timezone import localtime

from .mixins import ImageSerializerMixin
from backend.models import Author, Book, StatusLog, Note, BookAuthorRelation

from datetime import date, datetime, timedelta

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
            raise ValidationError('自ユーザーが作成した本を選択してください。')

        return data

    def validate_position(self, value):
        if value < 0:
            raise ValidationError('0以上の整数を入力してください。')
        return value

    def validate(self, data):
        position = data.get('position') or 0
        book = data.get('book')
        if book is None:
            instance = getattr(self, 'instance', None)
            book = instance.book

        if position > book.total:
            raise ValidationError({'position': '位置の指定が不正です。'})
        return data


class PageCountSerializerMixin():
    """ページ数カウント用 ミックスイン"""

    def _get_diff(self, instance: StatusLog, prev_status: StatusLog):
        book, position = instance.book, instance.position

        prev_position = 0
        for state in prev_status:
            if state.position > 0:
                prev_position = state.position
                break

        if position > prev_position:
            diff = position - prev_position
        else:
            diff = 0

        percentage = diff / book.total
        page = math.ceil(book.total_page * percentage) if book.format_type == 1 else diff

        return {
            'value': diff,
            'percentage': int(percentage * 100),
            'page': page
        }

    def _get_diff_total(self, status_log: StatusLog, date_threshold=None):
        """進捗の累計ページ数を取得"""

        total, total_threshold = [0] * 2
        for status in status_log:
            book, created_at = status.book, status.created_at
            prev_status = book.status_log.filter(created_at__lt=created_at).order_by('-created_at')
            total += self._get_diff(status, prev_status)['page']

            # 閾値の日付が指定されていた場合、閾値までの累計ページ数を取得
            if date_threshold and date_threshold <= localtime(created_at).date():
                total_threshold = total

        return [total, total_threshold] if date_threshold else total


class StatusLogSerializer(BookIncludedSerializer, PageCountSerializerMixin):
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
        prev_status = None

    def to_representation(self, instance):
        # ページ数カウント用: 事前にprev_statusを用意しておく
        book, created_at = instance.book, instance.created_at
        self.Meta.prev_status = book.status_log.filter(created_at__lt=created_at).order_by('-created_at')

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
        return self._get_diff(instance, self.Meta.prev_status)

    def get_position(self, instance):
        book, position = instance.book, instance.position

        if position == 0:
            # 積読中の場合、進捗の位置はその本の直前のステータスを参照する
            for state in self.Meta.prev_status:
                if state.position > 0:
                    position = state.position
                    break

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
        child=serializers.CharField(max_length=100), write_only=True,
        default=serializers.CreateOnlyDefault(['不明'])
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
            del ret['note'], ret['status']
        return ret

    def _get_or_create_authors(self, authors_name):
        authors = []

        # 関連先のAuthorオブジェクトを登録
        for name in authors_name:
            author, created = Author.objects.get_or_create(name=name)
            authors.append(author)

        return authors

    def create(self, validated_data):
        authors_name = validated_data.pop('authors')
        authors = self._get_or_create_authors(authors_name)

        # 登録したAuthorオブジェクトをbookに紐付けする
        book = super().create(validated_data)

        for i, author in enumerate(authors):
            BookAuthorRelation.objects.create(order=i, book=book, author=author)

        return book

    def update(self, instance, validated_data):
        authors_name = validated_data.get('authors')

        if authors_name:
            authors = self._get_or_create_authors(authors_name)

            del validated_data['authors']
            book = super().update(instance, validated_data)

            # 事前に中間テーブルを削除しておく
            BookAuthorRelation.objects.filter(book=book).delete()

            for i, author in enumerate(authors):
                BookAuthorRelation.objects.create(order=i, book=book, author=author)

            # orphanedなAuthorオブジェクトを削除
            Author.objects.filter(books=None).delete()

        else:
            book = super().update(instance, validated_data)

        return book

    def validate_authors(self, values):
        """著者名の正規化"""

        if not len(values):
            authors = ['不明']
        else:
            authors = []
            for value in values:
                value = value.replace('　', ' ')
                value = re.sub(r'([亜-熙ぁ-んァ-ヶ]) ([亜-熙ぁ-んァ-ヶ])', r'\1\2', value)
                authors.append(value)

        return authors

    def validate_total(self, value):
        """ページ数 or 位置No総数のバリデーション"""

        if value <= 0:
            raise ValidationError('0より大きな整数を入力してください。')

        return value

    def validate(self, data):
        """Kindle本の場合: ページ数に対するバリデーション"""

        invalid_total_page = not data.get('total_page') or data.get('total_page') <= 0
        if data.get('format_type') == 1 and invalid_total_page:
            raise ValidationError({'total_page': '0より大きな整数を入力してください。'})

        return data

    def get_status(self, instance):
        status_log = instance.status_log.order_by('-created_at')

        if not self.context.get('inside'):
            data = StatusLogSerializer(status_log, many=True, read_only=True, context={'inside': True}).data
            return data
        else:
            return None

    def get_note(self, instance):
        if not self.context.get('inside'):
            notes = instance.notes.order_by('position')
            return NoteSerializer(notes, many=True, read_only=True, context={'inside': True}).data
        else:
            return None

    def get_thumbnail(self, instance):
        NO_COVER_IMAGE = 'https://dummyimage.com/140x185/c4c4c4/636363.png&text=No+Image'
        return instance.thumbnail or NO_COVER_IMAGE


class AnalyticsSerializer(serializers.Serializer, PageCountSerializerMixin):
    """分析用シリアライザ"""

    number_of_books = serializers.SerializerMethodField()
    pages_read = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()

    def _get_daterange_from_filterset(self):
        """filtersetから日付範囲を取得"""

        date_joined = self.context['request'].user.date_joined.date()

        if self.context.get('filterset'):
            created_at = self.context['filterset'].form.cleaned_data.get('created_at')

            has_start = hasattr(created_at, 'start') and isinstance(created_at.start, datetime)
            start_date = created_at.start.date() if has_start else date_joined

            has_stop = hasattr(created_at, 'stop') and isinstance(created_at.stop, datetime)
            end_date = created_at.stop.date() if has_stop else date.today()
        else:
            start_date, end_date = date_joined, date.today()

        return start_date, end_date

    def get_number_of_books(self, status_log: StatusLog):
        """ステータスごとの累計冊数を取得"""

        # status_logに関連づけられたbooksをまとめて取得
        user = self.context['request'].user

        # ステータスの対象にある本と、ステータスのない本を検索
        # BUG: クエリの関係上、積読状態を含む集計 (to_be_read/all) はフィルタによる範囲指定が効かない
        books = Book.objects.filter(
            Q(status_log__in=status_log) | Q(created_by=user, status_log=None)
        )

        return {
            'to_be_read': books.filter_by_state('to_be_read').count(),
            'reading': books.filter_by_state('reading').count(),
            'read': books.filter_by_state('read').count(),
            'all': books.filter_by_state('all').count()
        }

    def get_pages_read(self, status_log: StatusLog):
        """読書ページ数の累計と、一日毎の平均ページ数を取得"""

        # NOTE: total_pageの情報を持たないKindle本はカウントしない
        # TODO: Kindleの位置Noとページ数に固定の相関性はあるか？あとで調べる。

        # 全体の累計ページ数を取得
        total_for_avg = None
        date_joined = self.context['request'].user.date_joined.date()

        # 平均ページ数の計算は、フィルタで指定された日付範囲に依拠させる
        if self.context.get('filterset'):
            created_at = self.context['filterset'].form.cleaned_data.get('created_at')

            if hasattr(created_at, 'start') and isinstance(created_at.start, datetime):
                start_date = created_at.start.date()
            else:
                start_date = date_joined

            if hasattr(created_at, 'stop') and isinstance(created_at.stop, datetime):
                end_date = created_at.stop.date()
            else:
                end_date = date.today()

            threshold_date = date_joined if start_date >= date_joined else start_date
        else:
            # ユーザー情報から呼び出された場合、start_dateはユーザーの登録日
            start_date = date_joined
            end_date = date.today()
            threshold_date = start_date

        total, total_for_avg = self._get_diff_total(status_log, threshold_date)

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
        cur_date, continuous_list = None, []

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
                # リセット前にcontinuous_listに連続日数を追加
                continuous_list.append(continuous)
                continuous = 1

        # 記録がないか、日付範囲から直前の記録の日付の差から2日より多く空いている場合、continuousを0にする
        start_date, end_date = self._get_daterange_from_filterset()
        if cur_date is None or (end_date - cur_date).days > 1:
            continuous = 0

        continuous_list.append(continuous)

        return {
            'total': len(date_set),
            'continuous': continuous,
            'continuous_max': max(continuous_list)
        }


class AuthorSerializer(serializers.ModelSerializer):
    """著者名リスト用シリアライザ"""

    count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['name', 'count']

    def get_count(self, instance: Author):
        return instance.books__count


class PagesDailySerializer(serializers.Serializer, PageCountSerializerMixin):
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
        status_daily = []
        for status in queryset:
            if localtime(status.created_at).date() == date_created:
                status_daily.append(status)

        pages_daily = self._get_diff_total(status_daily)
        return pages_daily
