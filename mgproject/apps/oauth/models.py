from django.db import models

# Create your models here.
from mgproject.utils.basemodels import BaseModel


class QQAuthUser(BaseModel):
    user = models.ForeignKey('userapp.Users',on_delete=models.CASCADE)
    openid = models.CharField(max_length=64,db_index=True,verbose_name='openid')

    class Meta:
        db_table = 't_qq_user'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name