from django.urls import path
from core.views import AppUserListView

urlpatterns = [
    path('appusers/', AppUserListView.as_view(), name='appuser-list'),
]
