from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreatePasswordRetypeSerializer
from django.conf import settings
from djoser.conf import settings as djoser_settings

from backend.models import BookOrigin


class ImageSerializerMixin():
    def get_thumbnail(self, instance):
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
        return self.get_thumbnail(instance)


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
        return self.get_thumbnail(instance)


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


class BookOriginSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = BookOrigin
        fields = ['id', 'title', 'price', 'created_by', 'username']
        extra_kwargs = {'created_by': {'required': False, 'write_only': True}}

    def get_username(self, instance):
        if instance.created_by is None:
            return None
        return instance.created_by.username

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("価格は0以上を指定してください。")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)
