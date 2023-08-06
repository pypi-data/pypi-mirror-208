from pydantic import BaseModel


class TaxPredictParam(BaseModel):
    """
    税收分类识别服务 参数模型
    """
    # 序列化
    sn: str = None
    # 输入文本
    text: str = None


class OssZipDirParam(BaseModel):
    """
    OSS目录压缩
    """
    # 桶名称
    bucket_name: str = None
    # 待压缩对象前缀
    object_prefix: str = None
    # 最终输出对象名
    dist_object_name: str = None


class SkuSearchParam(BaseModel):
    """
    搜索同款商品参数
    """
    # 页码
    page: int = 1
    # 搜索关键字
    text: str = None
