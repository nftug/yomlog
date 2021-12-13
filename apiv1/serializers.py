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
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        if instance.position == 0:
            # 積読中の場合、進捗の位置はその本の直前のステータスを参照する
            prev_status = StatusLog.objects.filter(book=instance.book, created_at__lt=instance.created_at).order_by('-created_at').first()

            if prev_status:
                ret['position'] = prev_status.position

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


class NoteSerializer(PostSerializer):
    class Meta:
        model = Note
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
            'quote_text': {'required': False},
            'quote_image': {'required': False},
        }


class BookSerializer(PostSerializer):
    # created_by = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Book
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['authors'] = self.get_authors(instance)
        return ret

    def get_status(self, instance):
        status_log = instance.status_log.order_by('-created_at')
        data = StatusLogSerializer(status_log, many=True, read_only=True).data

        if not data:
            data = [{
                'id': None,
                'state': 'to_be_read',
                'position': 0,
                'created_at': instance.created_at,
                'book': instance.id,
            }]

        return data

    def get_authors(self, instance):
        return instance.authors.split(',')

    def get_notes(self, instance):
        notes = instance.notes.order_by('position')
        return NoteSerializer(notes, many=True, read_only=True).data
