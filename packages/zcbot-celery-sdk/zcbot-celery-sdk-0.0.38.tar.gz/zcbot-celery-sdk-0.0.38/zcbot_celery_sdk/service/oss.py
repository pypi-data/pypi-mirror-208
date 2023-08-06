from celery.utils.log import get_task_logger
from .base import BaseService
from ..model.callback import Callback
from ..model.param import OssZipDirParam

LOGGER = get_task_logger(__name__)


class OssService(BaseService):

    def zip_dir(self, task_params: OssZipDirParam = None, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='oss.zip_dir', task_params=task_params.dict(), callback=callback, **kwargs)
