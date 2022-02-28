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
    path('analytics/', views.AnalyticsAPIView.as_view()),
    path('author/', views.AuthorListAPIView.as_view()),
    path('pages/', views.PagesDailyAPIView.as_view()),
    path('inquiry/', views.InquiryCreateAPIView.as_view())
]
