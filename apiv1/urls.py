from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('books_origin', views.BookOriginViewSet)
router.register('books_copy', views.BookCopyViewSet)
router.register('status_log', views.StatusLogViewSet)

app_name = 'apiv1'
urlpatterns = [
    path('', include(router.urls)),
]
