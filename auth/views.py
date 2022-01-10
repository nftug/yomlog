from django.views import View
from django.http import JsonResponse


class SocialRedirectView(View):
    def get(self, request, *args, **kwargs):
        code, state = str(request.GET.get('code')), str(request.GET.get('state'))
        return JsonResponse({'code': code, 'state': state})
