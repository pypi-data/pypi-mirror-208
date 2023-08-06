from django.urls import path
from .views import check_view

urlpatterns = [
    path('check/', check_view),
]
