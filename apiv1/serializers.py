from rest_framework import serializers
from django.utils.timezone import localtime
from rest_framework.exceptions import ValidationError
from django.conf import settings

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


class BookIncludedSerializer(PostSerializer):
    def get_book(self, instance):
        book = instance.book
        return {
            'id': book.id,
            'title': book.title,
            'authors': book.authors,
            'format_type': book.format_type,
            'total': book.total
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not super().context.get('inside'):
            ret['book'] = self.get_book(instance)

        return ret


class StatusLogSerializer(BookIncludedSerializer):
    # created_by = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()
    diff = serializers.SerializerMethodField()

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
            prev_status = StatusLog.objects.filter(
                book=instance.book, created_at__lt=instance.created_at
            ).order_by('-created_at').first()

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

    def get_diff(self, instance):
        # 前回までに進んだページ数 or 位置No
        base_status = instance

        while True:
            prev_status = StatusLog.objects.filter(
                book=instance.book, created_at__lt=base_status.created_at
            ).order_by('-created_at').first()

            if not prev_status or prev_status.position > 0:
                break

            base_status = prev_status

        if prev_status and instance.position > prev_status.position:
            diff = instance.position - prev_status.position
        elif not prev_status:
            diff = instance.position
        else:
            diff = 0

        percent = '{}%'.format(int((diff / instance.book.total) * 100))

        return {'value': diff, 'percent': percent}

    def validate_book(self, data):
        if data.created_by != self.context['request'].user:
            raise ValidationError('自ユーザーが作成した本を選択してください')

        return data


class NoteSerializer(BookIncludedSerializer):
    class Meta:
        model = Note
        exclude = ['created_by']
        extra_kwargs = {
            'created_at': {'required': False, 'read_only': True},
            'quote_text': {'required': False},
            'quote_image': {'required': False},
        }

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        quote_image = ret['quote_image']
        if quote_image and quote_image.startswith('/'):
            ret['quote_image'] = '{}{}'.format(settings.HOST_URL, quote_image)
        return ret


class BookSerializer(PostSerializer):
    # created_by = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    note = serializers.SerializerMethodField()

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
        context = {'inside': True}
        data = StatusLogSerializer(status_log, many=True, read_only=True, context=context).data
        return data

    def get_authors(self, instance):
        return instance.authors.split(',')

    def get_note(self, instance):
        notes = instance.notes.order_by('position')
        context = {'inside': True}
        return NoteSerializer(notes, many=True, read_only=True, context=context).data
