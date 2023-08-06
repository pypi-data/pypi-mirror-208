from .base import BaseService
from ..model.callback import Callback
from ..model.param import TaxPredictParam


class TaxService(BaseService):

    def get_tax_by_baiwang(self, task_params: TaxPredictParam = None, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='tax.baiwang', task_params=task_params.dict(), callback=callback, **kwargs)

    def get_tax_by_demo(self, task_params: TaxPredictParam = None, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='tax.demo', task_params=task_params.dict(), callback=callback, **kwargs)
