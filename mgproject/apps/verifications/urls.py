from django.urls import re_path
from . import views

urlpatterns = [
    re_path('^imgcodes/(?P<uuid>[\w-]+)/$',views.ImgcodeView.as_view()),
    re_path('^smscodes/(?P<phone>1[35789]\d{9})/$',views.SMScodeView.as_view()),
    re_path('^check_smscode/(?P<phone>1[35789]\d{9})/$',views.CheckSMScode.as_view())
]
