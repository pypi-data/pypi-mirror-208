from typing import Dict, List, Union

from .base import BaseService
from ..model.callback import Callback
from ..model.param import TextParam


def _params_convert(task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]]):
    text_list = list()
    # 批量
    if isinstance(task_params, List):
        for task_param in task_params:
            if isinstance(task_param, TextParam):
                text_list.append(task_param.dict())
            elif isinstance(task_params, str):
                text_list.append({'text': task_params})
            else:
                text_list.append(task_param)
    else:
        # 单个
        if isinstance(task_params, TextParam):
            text_list.append(task_params.dict())
        elif isinstance(task_params, str):
            text_list.append({'text': task_params})
        else:
            text_list.append(task_params)

    return text_list


class StaplesSkuTagService(BaseService):

    def predict_catalog1(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.staples.catalog1', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)

    def predict_catalog4(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.staples.catalog4', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)

    def predict_catalog6(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.staples.catalog6', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)

    def predict_brand(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.staples.brand', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)


class JslinkSkuTagService(BaseService):

    def predict_catalog1(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.jslink.catalog1', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)

    def predict_catalog4(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.jslink.catalog4', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)

    def predict_brand(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.jslink.brand', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)


class ZjmiSkuTagService(BaseService):

    def predict_catalog1(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.zjmi.catalog1', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)

    def predict_catalog3(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.zjmi.catalog3', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)

    def predict_brand(self, task_params: Union[str, Dict, TextParam, List[Union[str, TextParam, Dict]]] = None, threshold: float = 0.7, callback: Callback = None, **kwargs):
        return self.get_client().apply(task_name='sku_tag.zjmi.brand', task_params={'text_list': _params_convert(task_params), 'threshold': threshold}, callback=callback, **kwargs)
