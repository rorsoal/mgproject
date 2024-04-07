from django.urls import path,re_path
from . import views

urlpatterns = [
    re_path('^$',views.IndexView.as_view(),name='index')
]