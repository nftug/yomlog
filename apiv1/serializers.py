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
                raise ValidationError({'position': '以前と同じ位置が指定されています'})

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


class BookCopySerializer(PostSerializer):
    # created_by = serializers.SerializerMethodField()
    title = serializers.ReadOnlyField(source='book_origin.title')
    authors = serializers.SerializerMethodField()
    thumbnail = serializers.ReadOnlyField(source='book_origin.thumbnail')
    status = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = BookCopy
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
        }

    def get_status(self, instance):
        # 詳細の場合: ステータスのリストを表示
        # NOTE: 積読状態の時、最新のpositionは0になる (クライアント側で次のレコードから取得する必要あり)
        if hasattr(instance, 'status_log'):
            status_log = instance.status_log.order_by('-created_at')
            return StatusLogSerializer(status_log, many=True, read_only=True).data
        else:
            return None

    def get_authors(self, instance):
        return instance.book_origin.authors.split(',')

    def get_notes(self, instance):
        notes = instance.notes.order_by('position')
        return NoteSerializer(notes, many=True, read_only=True).data


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
