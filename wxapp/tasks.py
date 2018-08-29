from config.celery import app

from b2c.wxapp.services import poll_audit_status


@app.task
def poll_audit_status_every_hour_task():
    """
    每小时轮询小程序的审核状态
    """
    poll_audit_status()
