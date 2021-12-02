from django_filters import rest_framework as django_filter
from django.db.models import Q, F, Max

from backend.models import BookOrigin, BookCopy, StatusLog, Note


class GenericSearchFilterSet(django_filter.FilterSet):
    """検索用フィルタセット ミックスイン"""

    q = django_filter.CharFilter(label='Search', method='filter_search')

    class Meta:
        fields_for_search = []

    def filter_search(self, queryset, name, value):
        query = Q()
        words = value.split()

        for word in words:
            query_tmp = Q()

            for field in self.Meta.fields_for_search:
                query_tmp |= Q(**{field: word})

            query &= query_tmp

        return queryset.filter(query)


class BookOriginFilter(GenericSearchFilterSet):
    """BookOrigin 検索用フィルタ"""

    title = django_filter.CharFilter(field_name='title', lookup_expr='icontains')
    authors = django_filter.CharFilter(field_name='authors', lookup_expr='icontains')
    amazon_dp = django_filter.CharFilter(field_name='books_copy__amazon_dp')
    can_copy = django_filter.BooleanFilter(label='Can copy', method='filter_can_copy')

    class Meta:
        model = BookOrigin
        exclude = ['thumbnail']
        fields_for_search = [
            'title__icontains',
            'authors__icontains',
            'books_copy__amazon_dp'
        ]

    def filter_can_copy(self, queryset, name, value):
        # BookCopyを所持していない = BookCopyが作成可能なレコードのみ表示
        if value:
            return queryset.exclude(books_copy__created_by=self.request.user)
        else:
            return queryset


class BookCopyFilter(GenericSearchFilterSet):
    """BookCopy 検索用フィルタ"""

    STATUS_CHOICES = (('to_be_read', 'To be read'), ('reading', 'Reading'), ('read', 'Read'))

    title = django_filter.CharFilter(field_name='book_origin__title', lookup_expr='icontains')
    authors = django_filter.CharFilter(field_name='book_origin__authors', lookup_expr='icontains')
    status = django_filter.ChoiceFilter(label='Status', choices=STATUS_CHOICES, method='filter_status')

    class Meta:
        model = BookCopy
        fields = '__all__'
        fields_for_search = [
            'book_origin__title__icontains',
            'book_origin__authors__icontains',
            'amazon_dp'
        ]

    def filter_search(self, queryset, name, value):
        queryset = super().filter_search(queryset, name, value)
        return queryset.annotate(last_status_date=Max('status_log__created_at')).order_by('-last_status_date', '-created_at')

    def filter_status(self, queryset, name, value):
        # -FIXME: 最初のレコードではなくすべてのレコードを走査してしまう
        # →status_logの先頭レコードで検索するカスタムフィルタを作成して解決

        if not value:
            return queryset

        # TODO: filter_statusと合わせて2回ループを回すので、パフォーマンス面での不安はある
        query = Q(id=None)
        for book_copy in queryset:
            query |= Q(id=book_copy.id)

        if value == 'to_be_read':
            queryset = BookCopy.objects.filter_current_status(query, 'to_be_read')
        elif value == 'reading':
            queryset = BookCopy.objects.filter_current_status(query, 'reading')
        elif value == 'read':
            queryset = BookCopy.objects.filter_current_status(query, 'read')

        return queryset.annotate(last_status_date=Max('status_log__created_at')).order_by('-last_status_date', '-created_at')


class StatusLogFilter(GenericSearchFilterSet):
    """StatusLog 検索用フィルタ"""

    title = django_filter.CharFilter(field_name='book__book_origin__title', lookup_expr='icontains')
    authors = django_filter.CharFilter(field_name='book__book_origin__authors', lookup_expr='icontains')
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

    title = django_filter.CharFilter(field_name='book__book_origin__title', lookup_expr='icontains')
    authors = django_filter.CharFilter(field_name='book__book_origin__authors', lookup_expr='icontains')
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
