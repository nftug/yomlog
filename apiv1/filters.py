from django.db.models.query import QuerySet
from django_filters import rest_framework as django_filter
from django.db.models import Q, F, Max

from backend.models import Book, StatusLog, Note
import re


class GenericSearchFilterSet(django_filter.FilterSet):
    """検索用フィルタセット ミックスイン"""

    q = django_filter.CharFilter(label='Search', method='filter_search')
    q_or = django_filter.CharFilter(label='Search (OR)', method='filter_search_or')

    class Meta:
        fields_for_search = []

    def filter_search(self, queryset, name, value):
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

        return queryset.filter(query)

    def filter_search_or(self, queryset: QuerySet, name, value):
        return queryset | self.filter_search(queryset.model.objects.all(), name, value)


class BookFilter(GenericSearchFilterSet):
    """Book 検索用フィルタ"""

    STATUS_CHOICES = (('to_be_read', 'To be read'), ('reading', 'Reading'), ('read', 'Read'))

    title = django_filter.CharFilter(field_name='title', method='filter_search')
    authors = django_filter.CharFilter(field_name='authors', method='filter_search')
    title_or = django_filter.CharFilter(field_name='title', label='Title (OR)', method='filter_search_or')
    authors_or = django_filter.CharFilter(field_name='authors', label='Authors (OR)', method='filter_search_or')
    status = django_filter.ChoiceFilter(label='Status', choices=STATUS_CHOICES, method='filter_status')

    class Meta:
        model = Book
        fields = '__all__'
        fields_for_search = [
            'title__icontains',
            'authors__icontains',
            'amazon_dp'
        ]

    def filter_search(self, queryset, name, value):
        queryset = super().filter_search(queryset, name, value)
        return queryset.annotate(last_status_date=Max('status_log__created_at')).order_by('-last_status_date', '-created_at')

    def filter_search_or(self, queryset, name, value):
        queryset = super().filter_search_or(queryset, name, value)
        return queryset.annotate(last_status_date=Max('status_log__created_at')).order_by('-last_status_date', '-created_at')

    def filter_status(self, queryset, name, value):
        # -FIXME: 最初のレコードではなくすべてのレコードを走査してしまう
        # →status_logの先頭レコードで検索するカスタムフィルタを作成して解決

        if not value:
            return queryset

        if value == 'to_be_read':
            queryset = Book.objects.filter_current_status(queryset, 'to_be_read')
        elif value == 'reading':
            queryset = Book.objects.filter_current_status(queryset, 'reading')
        elif value == 'read':
            queryset = Book.objects.filter_current_status(queryset, 'read')

        return queryset.annotate(last_status_date=Max('status_log__created_at')).order_by('-last_status_date', '-created_at')


class StatusLogFilter(GenericSearchFilterSet):
    """StatusLog 検索用フィルタ"""

    title = django_filter.CharFilter(field_name='book__title', method='filter_search')
    authors = django_filter.CharFilter(field_name='book__authors', method='filter_search')
    title_or = django_filter.CharFilter(field_name='book__title', label='Title (OR)', method='filter_search_or')
    authors_or = django_filter.CharFilter(field_name='book__authors', label='Authors (OR)', method='filter_search_or')
    amazon_dp = django_filter.CharFilter(field_name='book__amazon_dp')
    created_by = django_filter.CharFilter(field_name='created_by__username')

    class Meta:
        model = StatusLog
        fields = '__all__'
        fields_for_search = [
            'book__title__icontains',
            'book__authors__icontains',
            'amazon_dp'
        ]


class NoteFilter(GenericSearchFilterSet):
    """Note 検索用フィルタ"""

    title = django_filter.CharFilter(field_name='book__title', method='filter_search')
    authors = django_filter.CharFilter(field_name='book__authors', method='filter_search')
    content = django_filter.CharFilter(field_name='content', method='filter_search')
    quote_text = django_filter.CharFilter(field_name='quote_text', method='filter_search')
    title_or = django_filter.CharFilter(field_name='book__title', label='Title (OR)', method='filter_search_or')
    authors_or = django_filter.CharFilter(field_name='book__authors', label='Authors (OR)', method='filter_search_or')
    content_or = django_filter.CharFilter(field_name='content', label='Content (OR)', method='filter_search_or')
    quote_text_or = django_filter.CharFilter(field_name='quote_text', label='Quote (OR)', method='filter_search_or')
    amazon_dp = django_filter.CharFilter(field_name='book__amazon_dp')
    created_by = django_filter.CharFilter(field_name='created_by__username')

    class Meta:
        model = Note
        exclude = ['quote_image']
        fields_for_search = [
            'book__title__icontains',
            'book__authors__icontains',
            'quote_text__icontains',
            'content__icontains'
        ]
