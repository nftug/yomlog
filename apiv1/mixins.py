from django.conf import settings
import os
from typing import List, Any
from collections import OrderedDict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework import response


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


class ListPaginator:
    """
    生のデータをページネーションに対応させる
    (See: https://stackoverflow.com/questions/38284440/drf-pagination-without-queryset)
    """

    def __init__(self, request: Request):
        # Hidden HtmlRequest properties/methods found in Request.
        self._url_scheme = request.scheme
        self._host = request.get_host()
        self._path_info = request.path_info

    def paginate_list(self, data: List[Any], page_size: int, page_number: Any) -> response.Response:
        paginator = Paginator(data, page_size)

        try:
            page = paginator.page(page_number)
        except (EmptyPage, PageNotAnInteger):
            raise ValidationError({'detail': '不正なページ数です。'})

        previous_url = None
        next_url = None
        if self._host and self._path_info:
            if page.has_previous():
                previous_url = '{}://{}{}?limit={}&page={}'.format(
                    self._url_scheme, self._host, self._path_info, page_size, page.previous_page_number())
            if page.has_next():
                next_url = '{}://{}{}?limit={}&page={}'.format(self._url_scheme, self._host, self._path_info, page_size, page.next_page_number())

        response_dict = OrderedDict([
            ('next', next_url),
            ('previous', previous_url),
            ('count', len(data)),
            ('totalPages', paginator.num_pages),
            ('results', page.object_list)
        ])
        return response.Response(response_dict)
