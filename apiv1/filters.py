from django.db.models.query import QuerySet
from django_filters import rest_framework as django_filter
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from backend.models import Book, StatusLog, Note, Author
import re


class GenericSearchFilterSet(django_filter.FilterSet):
    """検索用フィルタセット ミックスイン"""

    q = django_filter.CharFilter(label='Search', method='filter_search')
    q_or = django_filter.CharFilter(label='Search (OR)', method='filter_search_or')

    class Meta:
        fields_for_search = []

    def _clean_fields_for_search(self):
        if self.form.cleaned_data.get('book'):
            # 本が指定されている場合、フリーワードの検索基準から本の情報を除外する
            fields = self.Meta.fields_for_search
            try:
                fields.remove('book__title__icontains')
                fields.remove('book__authors__name__icontains')
            except ValueError:
                pass

    def filter_search(self, queryset, name, value):
        # フィールドの正規化
        self._clean_fields_for_search()

        query = Q()
        value = value.replace('　', ' ')
        name = re.sub('_or$', '', name)
        words = value.split()
        is_or = False

        for word in words:
            # ORキーワードの判定
            if word == 'OR':
                is_or = True
                continue

            # クエリの生成
            if name == 'q':
                query_tmp = Q(id=None)
                for field in self.Meta.fields_for_search:
                    query_tmp |= Q(**{field: word})
            else:
                query_tmp = Q(**{name + '__icontains': word})

            # is_orのフラグで分岐し、前のクエリとつなげる
            if is_or:
                query |= query_tmp
                is_or = False
            else:
                query &= query_tmp

        return queryset.filter(query).distinct()

    def filter_search_or(self, queryset: QuerySet, name, value):
        return queryset | self.filter_search(queryset.model.objects.all(), name, value)


class GenericEventFilterSet(django_filter.FilterSet):
    """イベント用フィルタ ミックスイン"""

    def filter_date_range(self, queryset, name, value):
        if name.startswith('accessed_at'):
            if hasattr(queryset, 'annotate_accessed_at'):
                queryset = queryset.annotate_accessed_at()
            else:
                raise ValidationError('アクセス日のフィールドが存在しません。')

        if value.start:
            queryset = queryset.filter(**{f'{name}__date__gte': value.start})
        if value.stop:
            queryset = queryset.filter(**{f'{name}__date__lte': value.stop})

        return queryset


class BookFilter(GenericSearchFilterSet, GenericEventFilterSet):
    """Book 検索用フィルタ"""

    STATUS_CHOICES = (('to_be_read', 'To be read'), ('reading', 'Reading'), ('read', 'Read'))

    title = django_filter.CharFilter(field_name='title', method='filter_search')
    authors = django_filter.CharFilter(field_name='authors__name', method='filter_search')
    title_or = django_filter.CharFilter(field_name='title', label='Title (OR)', method='filter_search_or')
    authors_or = django_filter.CharFilter(field_name='authors__name', label='Authors (OR)', method='filter_search_or')
    status = django_filter.ChoiceFilter(label='Status', choices=STATUS_CHOICES, method='filter_status')
    accessed_at = django_filter.DateFromToRangeFilter(
        label='最終アクセス日 (範囲指定)',
        method='filter_date_range',
    )
    created_at = django_filter.DateFromToRangeFilter(
        label='作成日 (範囲指定)',
        method='filter_date_range',
    )

    class Meta:
        model = Book
        fields = '__all__'
        fields_for_search = [
            'title__icontains',
            'authors__name__icontains',
            'amazon_dp'
        ]

    def filter_status(self, queryset, name, value):
        return queryset.filter_by_state(value)


class StatusLogFilter(GenericSearchFilterSet, GenericEventFilterSet):
    """StatusLog 検索用フィルタ"""

    title = django_filter.CharFilter(field_name='book__title', method='filter_search')
    authors = django_filter.CharFilter(field_name='book__authors__name', method='filter_search')
    title_or = django_filter.CharFilter(field_name='book__title', label='Title (OR)', method='filter_search_or')
    authors_or = django_filter.CharFilter(field_name='book__authors__name', label='Authors (OR)', method='filter_search_or')
    amazon_dp = django_filter.CharFilter(field_name='book__amazon_dp')
    created_by = django_filter.CharFilter(field_name='created_by__username')
    only_progress = django_filter.BooleanFilter(label='Not include "to be read"', method='filter_only_progress')
    created_at = django_filter.DateFromToRangeFilter(
        label='作成日 (範囲指定)',
        method='filter_date_range',
    )

    class Meta:
        model = StatusLog
        fields = '__all__'
        fields_for_search = [
            'book__title__icontains',
            'book__authors__name__icontains',
        ]

    def filter_only_progress(self, queryset, name, value):
        # 積読状態を除いたステータスを取得

        if not value:
            return queryset

        return queryset.exclude(position=0)


class NoteFilter(GenericSearchFilterSet, GenericEventFilterSet):
    """Note 検索用フィルタ"""

    title = django_filter.CharFilter(field_name='book__title', method='filter_search')
    authors = django_filter.CharFilter(field_name='book__authors__name', method='filter_search')
    content = django_filter.CharFilter(field_name='content', method='filter_search')
    quote_text = django_filter.CharFilter(field_name='quote_text', method='filter_search')
    title_or = django_filter.CharFilter(field_name='book__title', label='Title (OR)', method='filter_search_or')
    authors_or = django_filter.CharFilter(field_name='book__authors__name', label='Authors (OR)', method='filter_search_or')
    content_or = django_filter.CharFilter(field_name='content', label='Content (OR)', method='filter_search_or')
    quote_text_or = django_filter.CharFilter(field_name='quote_text', label='Quote (OR)', method='filter_search_or')
    amazon_dp = django_filter.CharFilter(field_name='book__amazon_dp')
    created_by = django_filter.CharFilter(field_name='created_by__username')

    class Meta:
        model = Note
        exclude = ['quote_image']
        fields_for_search = [
            'book__title__icontains',
            'book__authors__name__icontains',
            'quote_text__icontains',
            'content__icontains'
        ]
