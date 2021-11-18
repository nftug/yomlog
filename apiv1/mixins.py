from rest_framework import serializers
from django.conf import settings
import os


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
