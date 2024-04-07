import os
import sys

# 添加导包路径
B_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(1, B_DIR)
sys.path.insert(0, os.path.join(B_DIR, 'utils'))

import logging
from celery_tasks.main import celery_app

# 为celery使用django配置文件进行设置
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.dev')

from huyi_sms.sms3 import send_sms_code

logger = logging.getLogger('django')


@celery_app.task(name='huyi_send_sms_code')
def huyi_send_sms_code(phone, smscode_str):
    """
    发送短信异步任务
    :param phone: 手机号
    :param smscode: 短信验证码
    :return: 成功 code=2 或 失败 smsid=0
    """

    try:
        # 调用外部接口执行发送短信任务
        ret = send_sms_code(smscode_str, phone)

    except Exception as e:
        logger.error(e)

    if ret.get('code') != 2:
        logger.error(e)

    return ret.get('code', None)