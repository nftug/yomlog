from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreatePasswordRetypeSerializer
from django.conf import settings
from djoser.conf import settings as djoser_settings
import os

from backend.models import *


class ImageSerializerMixin():
    def _get_thumbnail(self, instance):
        url = None

        if hasattr(instance, 'photo') and instance.photo:
            url = instance.photo.url
        elif hasattr(instance, 'avatar') and instance.avatar:
            url = instance.avatar.url

        if url is not None:
            if not settings.DEBUG:
                CLOUDINARY_URL = 'https://res.cloudinary.com/' + os.environ['CLOUDINARY_CLOUD_NAME'] + '/image/upload'
                if hasattr(instance, 'avatar'):
                    prop = '/c_fill,h_128,w_128'
                else:
                    prop = '/c_fill,w_350'

                url = url.replace(CLOUDINARY_URL, CLOUDINARY_URL + prop)

            else:
                url = '{}{}'.format(settings.HOST_URL, url)

        return url


class PostSerializer(serializers.ModelSerializer, ImageSerializerMixin):
    def _get_user_profile(self, user):
        ret = {}

        if user is None:
            ret['username'] = None
            ret['fullname'] = None
            ret['avatar'] = None
        else:
            ret['username'] = user.username
            fullname = '{} {}'.format(user.last_name, user.first_name).strip()
            ret['fullname'] = fullname if fullname else user.username
            ret['avatar'] = self._get_thumbnail(user)

        return ret

    def get_created_by(self, instance):
        return self._get_user_profile(instance.created_by)

    def create(self, validated_data):
        user = super().context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)


class CustomUserSerializer(UserSerializer, ImageSerializerMixin):
    fullname = serializers.SerializerMethodField()
    avatar_thumbnail = serializers.SerializerMethodField()

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
            'avatar_thumbnail'
        )
        read_only_fields = (djoser_settings.LOGIN_FIELD, 'is_superuser', 'username')

    def get_fullname(self, instance):
        fullname = '{} {}'.format(instance.last_name, instance.first_name).strip()
        return fullname if fullname else instance.username

    def get_avatar_thumbnail(self, instance):
        return self._get_thumbnail(instance)


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
            'avatar'
        )

    def create(self, validated_data):
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


class StatusLogSerializer(PostSerializer):
    created_by = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = StatusLog
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def get_status(self, instance):
        if not instance.position:
            # TODO: ここは現在表示されない。要対策？
            return 'to_be_read'
        elif instance.position < instance.book.total:
            return 'reading'
        else:
            return 'done'


class BookCopySerializer(PostSerializer):
    created_by = serializers.SerializerMethodField()
    title = serializers.CharField(source='book_origin.title')
    author = serializers.CharField(source='book_origin.author')
    thumbnail = serializers.CharField(source='book_origin.thumbnail')
    status = serializers.SerializerMethodField()

    class Meta:
        model = BookCopy
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def get_status(self, instance):
        context = {'request': self.context.get('request')}
        status = instance.status_log.order_by('-created_at').first()
        return StatusLogSerializer(status, many=False, read_only=True, context=context).data


class BookOriginSerializer(PostSerializer):
    created_by = serializers.SerializerMethodField()
    books_copy = serializers.SerializerMethodField()

    class Meta:
        model = BookOrigin
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True}
        }

    def get_books_copy(self, instance):
        books_copy = BookCopy.objects.filter(book_origin=instance)
        return (_.id for _ in books_copy)
