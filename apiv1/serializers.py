from rest_framework import serializers
from django.utils.timezone import localtime

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
    created_by = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = StatusLog
        fields = '__all__'
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
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
        status_log = instance.status_log.order_by('-created_at')

        if status_log.exists():
            if status_log.count() > 1:
                context['status_previous'] = status_log[1]

            return StatusLogSerializer(status_log.first(), many=False, read_only=True, context=context).data
        else:
            return {
                'state': 'to_be_read',
                'id': None,
                'position': 0,
                'created_at': None,
                'book': instance.id
            }


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
