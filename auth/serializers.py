from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreatePasswordRetypeSerializer
from djoser.conf import settings as djoser_settings
from datetime import date, timedelta

from apiv1.mixins import ImageSerializerMixin
from apiv1.serializers import AnalyticsSerializer, BookSerializer, AuthorSerializer, PagesDailySerializer
from backend.models import StatusLog, Book, Author


class CustomUserSerializer(UserSerializer, ImageSerializerMixin):
    fullname = serializers.SerializerMethodField()
    avatar_thumbnail = serializers.SerializerMethodField()
    analytics = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = tuple(get_user_model().REQUIRED_FIELDS) + (
            djoser_settings.USER_ID_FIELD,
            djoser_settings.LOGIN_FIELD,
            'username',
            'is_superuser',
            'first_name',
            'last_name',
            'fullname',
            'avatar',
            'avatar_thumbnail',
            'date_joined',
            'analytics'
        )
        read_only_fields = (djoser_settings.LOGIN_FIELD, 'is_superuser', 'username')

    def get_fullname(self, instance):
        fullname = '{} {}'.format(instance.last_name, instance.first_name).strip()
        return fullname if fullname else instance.username

    def get_avatar_thumbnail(self, instance):
        return self._get_thumbnail(instance)

    def get_analytics(self, instance):
        status_log = StatusLog.objects.filter(created_by=instance, position__gt=0).select_related('book')
        context = {**self.context, 'userinfo': True}
        analytics = AnalyticsSerializer(status_log, context=context).data

        # recent_booksの先頭5件を取得
        books = Book.objects.filter(created_by=instance).sort_by_accessed_at()
        recent_books = BookSerializer(books[:5], many=True, context={'inside': True}).data

        # authors_countの先頭8件を取得
        user = self.context['request'].user
        authors = Author.objects.filter(books__created_by=user).sort_by_books_count()[:8]
        authors_count = AuthorSerializer(authors, many=True, context=context).data

        # 直近一週間に読んだページ数を取得
        date_week_ago = date.today() - timedelta(days=7)
        status_log = status_log.filter(created_at__date__gte=date_week_ago)
        pages_daily = PagesDailySerializer(status_log, context=context).data

        return {
            **analytics,
            'recent_books': recent_books,
            'authors_count': authors_count,
            **pages_daily
        }


class CustomUserListSerializer(CustomUserSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'username',
            'fullname',
            'avatar'
        )

    def get_avatar(self, instance):
        return self._get_thumbnail(instance)


class CustomUserCreateSerializer(UserCreatePasswordRetypeSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            djoser_settings.LOGIN_FIELD,
            djoser_settings.USER_ID_FIELD,
            'first_name',
            'last_name',
            'password',
            'avatar',
            'is_active'
        )
        read_only_fields = ('is_active',)

    def create(self, validated_data):
        if validated_data.get('email'):
            # メールアドレスからユーザー名を生成
            username_base = validated_data['email'].split('@')[0]
            user_model = get_user_model()

            username = username_base
            n = 1

            while user_model.objects.filter(username=username).exists():
                n += 1
                username = '{}-{}'.format(username_base, n)

            validated_data['username'] = username

        return super().create(validated_data)
