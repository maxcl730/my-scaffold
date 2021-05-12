from extensions import flask_celery
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@flask_celery.task(
    name = 'tasks.log_userid',
    bind=True,
    ignore_result=True,
    default_retry_delay=300,
    max_retries=3)
def log_userid(user):
    logger.info("Current user's id is [{}]".format(user.id))

