from typing import Union, Callable, Dict, List, Any
from pydantic import BaseModel

from ..common.utils import obj_to_ref


class Callback(BaseModel):
    """
    结果回调元数据
    """
    # 调用方应用编码
    app_code: str = None
    # 回调数据
    callback_data: Union[str, Dict, List] = None
    # 回调函数
    callback_func: Union[str, Callable] = None
    # 消息标签
    tags: Union[str, List] = None
    # 调用方应用租户编码
    tenant_code: str = None

    def __init__(self, func: Union[str, Callable] = None, data: Union[str, Dict, List] = None, app_code: str = None, **kw: Any):
        super().__init__(**kw)
        if func:
            if isinstance(func, str):
                self.callback_func = func
            else:
                self.callback_func = obj_to_ref(func)
        self.callback_data = data
        self.app_code = app_code

    def set_func(self, func: Union[str, Callable]):
        if isinstance(func, str):
            self.callback_func = func
        else:
            self.callback_func = obj_to_ref(func)

        return self

    def set_data(self, data: Union[str, Dict, List]):
        self.callback_data = data

        return self
