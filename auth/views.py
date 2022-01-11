from rest_framework import serializers, status, views, response
from rest_framework.exceptions import ValidationError
from .serializers import TwitterOAuthTokenSerializer


class TwitterOAuthTokenAPIView(views.APIView):
    """TwitterのOAuthトークン取得用 API"""

    def post(self, request, *args, **kwargs):
        context = {'request': request}
        serializer = TwitterOAuthTokenSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data, status.HTTP_200_OK)
