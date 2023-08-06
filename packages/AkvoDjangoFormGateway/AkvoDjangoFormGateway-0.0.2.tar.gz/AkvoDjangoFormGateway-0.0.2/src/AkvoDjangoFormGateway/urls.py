from django.urls import path, include
from .views import AkvoFormViewSet, CheckView

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'forms', AkvoFormViewSet, basename='forms')
urlpatterns = [
    path('', include(router.urls)),
    path('check/', CheckView.as_view()),
]
