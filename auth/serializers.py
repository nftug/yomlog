from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreatePasswordRetypeSerializer
from djoser.conf import settings as djoser_settings
from rest_framework.exceptions import ValidationError

from apiv1.mixins import ImageSerializerMixin
from apiv1.serializers import AnalyticsSerializer, BookSerializer
from backend.models import StatusLog, Book


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
        queryset = StatusLog.objects.filter(created_by=instance, position__gt=0).select_related('book')
        context = {**self.context, 'userinfo': True}
        analytics = AnalyticsSerializer(queryset, context=context).data

        # recent_booksの先頭5件を取得
        books = Book.objects.filter(created_by=instance).sort_by_accessed_at()[:5]
        recent_books = BookSerializer(books, many=True, context={'inside': True}).data
        return {**analytics, 'recent_books': recent_books}


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
