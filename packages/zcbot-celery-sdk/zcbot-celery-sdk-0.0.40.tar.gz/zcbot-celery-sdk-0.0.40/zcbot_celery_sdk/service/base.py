from ..client import CeleryClient, CeleryClientHolder


class BaseService(object):
    """
    基础服务
    """

    def __init__(self, celery_client: CeleryClient = None):
        self.celery_client = celery_client

    def get_client(self):
        return self.celery_client or CeleryClientHolder.get_default_instance()

