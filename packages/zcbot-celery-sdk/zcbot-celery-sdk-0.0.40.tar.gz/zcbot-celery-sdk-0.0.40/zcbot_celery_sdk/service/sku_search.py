from typing import Dict

from .base import BaseService
from ..model.callback import Callback
from ..model.param import SkuSearchParam


class SkuSearchService(BaseService):
    """
    商品搜索服务
    """

    def search(self, platform: str = None, task_params: SkuSearchParam = None, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name=f'sku_search.{platform}', task_params=task_params, callback=callback, **kwargs)

    def search_jd_pc(self, task_params: SkuSearchParam = None, callback: Callback = None, **kwargs):
        """
        【商品搜索】京东PC端
        """
        return self.get_client().apply(task_name='sku_search.jd_pc', task_params=task_params.dict(), callback=callback, **kwargs)

    def search_sn_pc(self, task_params: SkuSearchParam = None, callback: Callback = None, **kwargs):
        """
        【商品搜索】苏宁PC端
        """
        return self.get_client().apply(task_name='sku_search.sn_pc', task_params=task_params.dict(), callback=callback, **kwargs)

    def search_mmb_pc(self, task_params: SkuSearchParam = None, callback: Callback = None, **kwargs):
        """
        【商品搜索】慢慢买PC端
        """
        return self.get_client().apply(task_name='sku_search.mmb_pc', task_params=task_params.dict(), callback=callback, **kwargs)

    def search_mmb_m(self, task_params: SkuSearchParam = None, callback: Callback = None, **kwargs):
        """
        【商品搜索】慢慢买手机端
        """
        return self.get_client().apply(task_name='sku_search.mmb_m', task_params=task_params.dict(), callback=callback, **kwargs)
