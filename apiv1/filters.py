from django_filters import rest_framework as django_filter
from django.db.models import Q
from django.db.models import F

from backend.models import BookOrigin, BookCopy


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
    author = django_filter.CharFilter(field_name='author', lookup_expr='icontains')
    amazon_dp = django_filter.CharFilter(field_name='books_copy__amazon_dp')
    can_copy = django_filter.BooleanFilter(label='Can copy', method='filter_can_copy')

    class Meta:
        model = BookOrigin
        exclude = ['thumbnail']
        fields_for_search = [
            'title__icontains',
            'author__icontains',
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
    author = django_filter.CharFilter(field_name='book_origin__author', lookup_expr='icontains')
    status = django_filter.ChoiceFilter(label='Status', choices=STATUS_CHOICES, method='filter_status')

    class Meta:
        model = BookCopy
        fields = '__all__'
        fields_for_search = [
            'book_origin__title__icontains',
            'book_origin__author__icontains',
            'amazon_dp'
        ]

    def filter_status(self, queryset, name, value):
        # FIXME: 最初のレコードではなくすべてのレコードを走査してしまう
        # WORKAROUND 1: read→readingになることはないと考える？
        # WORKAROUND 2: ModelManagerで専用のステータスを作成する

        if not value:
            return queryset

        # TODO: filter_statusと合わせて2回ループを回すので、パフォーマンス面での不安はある
        query = Q(id=None)
        for book_copy in queryset:
            query |= Q(id=book_copy.id)

        if value == 'to_be_read':
            queryset_tmp = queryset.filter(status_log=None)
        elif value == 'reading':
            queryset_tmp = BookCopy.objects.filter_current_status(query, 'reading')
        elif value == 'read':
            queryset_tmp = BookCopy.objects.filter_current_status(query, 'read')

        return queryset_tmp.filter(query)