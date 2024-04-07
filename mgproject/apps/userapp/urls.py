from django.contrib.auth.decorators import login_required
from django.urls import path,re_path
from . import views

urlpatterns = [
    re_path('^register/$',views.RegisterView.as_view()),
    re_path('^usernames/(?P<username>[a-zA-Z_]{5,8})/count/$',views.UsernameCount.as_view()),
    re_path('^phones/(?P<phone>1[35789][0-9]{9})/count/$',views.PhoneCount.as_view()),
    re_path('^logout/$',views.LogoutView.as_view()),
    re_path('^login/$',views.LoginView.as_view()),
    re_path('^usercenter/$',login_required(views.UserCenterView.as_view())),
    re_path('^emails/$',views.EmailView.as_view())
]