# -*- coding: utf-8 -*-



from flask_mail import Message

from app import config
from app import mail
from app import create_app

# Celery
from celery import Celery
celery = Celery('mail_task', broker=config.CELERY_BROKER_URL, backend=config.CELERY_RESULT_BACKEND)

@celery.task
def send_async_email(msg):
    app = create_app()
    # 注意：Flask-Mail 需要在应用的上下文中运行，因此在调用 send() 之前需要创建一个应用上下文
    with app.app_context():
        # 此异步调用返回值并不保留，因此应用本身无法知道是否调用成功或者失败。
        # 运行这个示例的时候，需要检查 celery worker 的输出来排查发送邮件过程是否有问题
        # celery worker -A app.tasks.celery --loglevel=info
        mail.send(Message(**msg))
