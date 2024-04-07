from django.contrib.auth.backends import ModelBackend
import re

from .models import Users


class MutiAccountLoginAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # 用户名参数进行多账户校验
            if re.match('^1[35789]\d{9}$',username):
                user = Users.objects.get(phone=username)
            else:
                user = Users.objects.get(username=username)
        except Users.DoesNotExist:
            user = None

        # 用户名和密码同时匹配校验
        if user and user.check_password(password):
            return user