import django_redis
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View
import string,random
from captcha.image import ImageCaptcha
import logging

from mgproject.utils.huyi_sms.sms3 import send_sms_code

logger = logging.getLogger('django')

class ImgcodeView(View):
    def get(self,request,uuid):
        """
        获取图片验证码资源
        :param request:
        :return:
        """
        # 随机生成验证码（四位数值类型）
        seed = string.digits  # '0123456789'
        r = random.choices(seed,k=4)  # ['7','5','3','2']
        imgcode_str = ''.join(r)  # '7532'

        # 根据1生成的数字创建图片验证码资源
        imgcode = ImageCaptcha().generate(chars=imgcode_str)

        # 将imgcode_str存入redis数据库中
        redis_conn = django_redis.get_redis_connection('verify_code')
        redis_conn.setex('img_%s'%uuid,300,imgcode_str)

        # 返回资源给前端
        return HttpResponse(imgcode,content_type='image/png')


class SMScodeView(View):
    def get(self,request,phone):
        """
        匹配并删除图形验证码
        发送短信验证码
        :param request:
        :param phone:
        :return:
        """
        # 1. 获取请求参数（路径参数+查询字符串）
        imgcode_client = request.GET.get('imgcode','')
        uuid = request.GET.get('uuid','')

        # 2. 校验参数(完整性判断)
        if not all([phone,imgcode_client,uuid]):
            return JsonResponse({'code':'4001','errormsg':'缺少必传参数'})

        # 建立redis数据库连接
        redis_conn = django_redis.get_redis_connection('verify_code')
        is_send = redis_conn.get('is_send_%s'%phone)

        # 获取is_send并且判断是否发送过于频繁
        if is_send:
            return JsonResponse({'code': '4004', 'errormsg': '发送短信验证码过于频繁'})


        # 3. 获取服务器生成的图片验证码

        imgcode_server = redis_conn.get('img_%s'%uuid)

        # 4. 匹配（非空判断/一致性判断）
        if imgcode_server is None:
            return JsonResponse({'code':'4002','errormsg':'图片验证码已过期'})

        imgcode_server = imgcode_server.decode('utf-8');
        print(imgcode_server)

        if imgcode_client.lower() != imgcode_server.lower():
            return JsonResponse({'code':'4003','errormsg':'图片验证码不一致'})

        # 5. 删除图片验证码（避免用户恶意测试）
        try:
            redis_conn.delete('img_%s'%uuid)
        except Exception as e:
            logger.error(e)


        # 6. 生成短信验证码(6位数字)
        seed = string.digits
        r = random.choices(seed,k=6)
        smscode_str = "".join(r)

        print('smscode:',smscode_str)

        # 7. 保存短信验证码到Redis数据库
        # redis_conn.setex('sms_%s'%phone,60,smscode_str)
        # redis_conn.setex('is_send_%s'%phone,60,1)

        # 获取管道对象
        pl = redis_conn.pipeline()
        pl.setex('sms_%s'%phone,60,smscode_str)
        pl.setex('is_send_%s'%phone,60,1)
        pl.execute()

        # 异步执行发送短信验证码功能

        # from mgproject.celery_tasks.sms.tasks import huyi_send_sms_code
        # # Celery异步发送短信验证码
        # ret = huyi_send_sms_code.delay(phone, smscode_str)
        #
        # # 8. 根据外部接口返回值响应前端结果
        # if ret:  # 执行一个任务就返回一个taskid 689e889c-a607-49f3-9777-248a8dcce310
        #     return JsonResponse({'code': '200', 'errormsg': 'OK'})
        # return JsonResponse({'code': '5001', 'errormsg': '发送短信验证码错误'})


        # 8. 发送短信验证码
        #ret = send_sms_code(smscode_str,phone)

        #9. 根据外部接口返回值响应前端结果
        ret = {'code':2}
        if ret.get('code') == 2:
            return JsonResponse({'code':'200','errormsg':'OK'})
        return JsonResponse({'code':'5001','errormsg':'发送短信验证码错误'})


class CheckSMScode(View):
    def get(self,request,phone):
        """
        用户注册时短信验证码校验
        :param request:
        :param phone:
        :return:
        """
        # 接收请求参数
        smscode_client = request.GET.get('smscode','')
        # 校验参数
        if not all([phone,smscode_client]):
            return JsonResponse({'code':'4001','errormsg':'缺少必传参数'})

        # 查询服务器端短信验证码
        redis_conn = django_redis.get_redis_connection('verify_code')
        smscode_server = redis_conn.get('sms_%s'%phone)


        # 匹配(非空判断/有效性判断)
        if smscode_server is None:
            return JsonResponse({'code':'4002','errormsg':'短信验证码失效'})
        smscode_server = smscode_server.decode('utf-8')

        if smscode_client != smscode_server:
            return  JsonResponse({'code':'4003','errormsg':'短信验证码不一致'})

        # 响应结果
        return JsonResponse({'code':'200','errormsg':'OK'})
