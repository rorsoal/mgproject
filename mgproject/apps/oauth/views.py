import re

from django import http
from django.contrib.auth import login
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views.generic.base import View
from AgentLogin import AgentLogin
from django.conf import settings
from django_redis import get_redis_connection

from .models import QQAuthUser
from .utils import generate_secret_openid, check_secret_openid
from  userapp.models import Users


class QQLoginURLView(View):
    def get(self,request):
        """
        获取QQ扫码登录链接地址
        :param request:
        :return:
        """
        qq_url = AgentLogin.qq_url(settings.QQ_CLIENT_ID,settings.QQ_REDIRECT_URI)

        return JsonResponse({'code':200,'errormsg':'OK','login_url':qq_url})

class QQAuthUserView(View):
    def get(self,request):
        """
        获取openid
        :param request:
        :return:
        """


        # 获取code参数
        code = request.GET.get('code','')

        # 校验参数
        if not code:
            return http.HttpResponseForbidden('缺少code参数值')

        # 调用接口方法获取openid
        nickname,openid = AgentLogin.qq(settings.QQ_CLIENT_ID,settings.QQ_APP_KEY,settings.QQ_REDIRECT_URI,code)

        # 通过openid判断当前QQ用户是否绑定项目用户
        try:
            qq_user = QQAuthUser.objects.get(openid=openid)
        except QQAuthUser.DoesNotExist:
            # QQ用户没有绑定项目用户

            # 加密openid数据
            sec_openid = generate_secret_openid(openid)

            # 传递加密数据给用户绑定页面
            return render(request,'oauth/oauth_user.html',{'sec_openid':sec_openid})

        else:
            # QQ用户已绑定项目用户

            # 获取关联的项目用户对象
            user = qq_user.user
            # 状态保持
            login(request,user)
            # 响应结果
            return redirect(reverse('newsapp:index'))

    def post(self,request):
        """
        将当前访问QQ用户绑定项目用户
        :param request:
        :return:
        """
        # 接收参数
        sec_openid = request.POST.get('sec_openid','')
        phone = request.POST.get('phone', '')
        sms_code_client = request.POST.get('msgcode', '')
        pwd = request.POST.get('password', '')

        # 校验参数(非空校验/格式校验/一致性校验)
        # 判断参数是否齐全
        if not all([phone, pwd, sms_code_client, sec_openid]):
            return http.HttpResponseForbidden('缺少必传参数')
        # 判断手机号是否合法
        if not re.match(r'^1[35789]\d{9}$', phone):
            return http.HttpResponseForbidden('请输入正确的手机号码')
        # 判断密码是否合法
        if not re.match(r'^[0-9A-Za-z]{3,8}$', pwd):
            return http.HttpResponseForbidden('请输入3,8位的密码')

        # 判断短信验证码是否一致
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % phone)
        if sms_code_server is None:
            return render(request, 'oauth/oauth_user.html', {'sms_code_errmsg': '无效的短信验证码'})
        if sms_code_client != sms_code_server.decode():
            return render(request, 'oauth/oauth_user.html', {'sms_code_errmsg': '输入短信验证码有误'})


        # 绑定用户

        # 判断当前QQ用户是否合法(解密openid数据)
        openid = check_secret_openid(sec_openid)

        if openid is None:
            return render(request, 'oauth/oauth_user.html', {'openid_errmsg': 'openid已经失效'})

        # 获取项目用户
        try:
            user = Users.objects.get(phone=phone)
        except Users.DoesNotExist:
            # 创建项目新用户
            user = Users.objects.create_user(username=phone,password=pwd,phone=phone)
        else:
            # 判断项目用户密码是否正确
            if not user.check_password(pwd):
                return render(request,'oauth/oauth_user.html',{'qq_login_errmsg':'用户名或密码错误'})

        # 绑定用户
        try:
            QQAuthUser.objects.create(user=user,openid=openid)
        except Exception:
            return render(request, 'oauth/oauth_user.html', {'reg_error_msg': '用户绑定失败'})

        # 状态保持
        login(request,user)

        # 响应结果
        return redirect(reverse('newsapp:index'))