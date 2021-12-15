from django.urls import path, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('book', views.BookViewSet)
router.register('status', views.StatusLogViewSet)
router.register('note', views.NoteViewSet)

app_name = 'apiv1'
urlpatterns = [
    path('', include(router.urls)),
]
