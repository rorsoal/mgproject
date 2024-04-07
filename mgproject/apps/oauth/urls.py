from django.urls import re_path
from . import views

urlpatterns = [
    re_path('^qq/login/$',views.QQLoginURLView.as_view()),
    re_path('^about/$',views.QQAuthUserView.as_view()),
]
