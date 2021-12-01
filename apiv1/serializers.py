from rest_framework import serializers
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError

from .mixins import ImageSerializerMixin
from backend.models import *
from auth.serializers import CustomUserListSerializer


class PostSerializer(serializers.ModelSerializer, ImageSerializerMixin):
    def get_created_by(self, instance):
        return CustomUserListSerializer(instance.created_by, many=False, read_only=True).data

    def create(self, validated_data):
        user = super().context['request'].user
        validated_data['created_by'] = user
        return super().create(validated_data)


class StatusLogSerializer(PostSerializer):
    # created_by = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = StatusLog
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
            'created_by': {'required': False, 'read_only': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        status_previous = self.context.get('status_previous')
        if instance.position == 0 and status_previous:
            # 積読中で前のレコードが存在する場合、前のレコードの値を返す
            ret['position'] = status_previous.position
            ret['created_at'] = localtime(status_previous.created_at)

        return ret

    def get_state(self, instance):
        if instance.position == 0:
            return 'to_be_read'
        elif instance.position < instance.book.total:
            return 'reading'
        else:
            return 'read'

    def validate_book(self, data):
        if data.created_by != self.context['request'].user:
            raise ValidationError('自ユーザーが作成した本を選択してください')

        return data

    def validate(self, data):
        status_log = data.get('book').status_log
        if status_log.exists():
            current_position = status_log.first().position
            if data.get('position') == current_position:
                raise ValidationError({'position': '以前と同じ位置情報が指定されています'})

        return data


class BookCopySerializer(PostSerializer):
    created_by = serializers.SerializerMethodField()
    title = serializers.ReadOnlyField(source='book_origin.title')
    authors = serializers.SerializerMethodField()
    thumbnail = serializers.ReadOnlyField(source='book_origin.thumbnail')
    status = serializers.SerializerMethodField()

    class Meta:
        model = BookCopy
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def get_status(self, instance):
        if hasattr(instance, 'status_log'):
            context = {'request': self.context.get('request')}
            status_log = instance.status_log.order_by('-created_at')

            if status_log.exists():
                if status_log.count() > 1:
                    context['status_previous'] = status_log[1]
                return StatusLogSerializer(status_log.first(), read_only=True, context=context).data

        return {
            'state': 'to_be_read',
            'id': None,
            'position': 0,
            'created_at': None,
            'book': instance.id if hasattr(instance, 'id') else None
        }

    def get_authors(self, instance):
        return instance.book_origin.authors.split(',')


class BookOriginSerializer(serializers.ModelSerializer):
    # books_copy = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    amazon_dp = serializers.SerializerMethodField()

    class Meta:
        model = BookOrigin
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True}
        }

    def get_amazon_dp(self, instance):
        if hasattr(instance, 'id'):
            books_copy = BookCopy.objects.filter(book_origin=instance).values('amazon_dp')
            return list(set((_['amazon_dp'] for _ in books_copy)))
        else:
            return []
