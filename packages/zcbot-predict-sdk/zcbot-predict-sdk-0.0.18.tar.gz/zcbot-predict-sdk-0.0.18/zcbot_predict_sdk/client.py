# -*- coding: utf-8 -*-
from redis import Redis
from typing import Callable, Dict, Union, List
from celery import Celery, Task, group
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from .common.exceptions import BizException
from .common.utils import obj_to_ref, singleton
from .common.keys import get_result_key
from .model.callback import Callback

LOGGER = get_task_logger(__name__)


# @singleton
class PredictClient(object):
    """
    Celery服务客户端
    注意：此类不建议手动初始化，可通过PredictClientHolder初始化，方便各service类自动获取
    """
    def __init__(self, celery_broker_url: str, celery_result_backend: str, monitor_redis_uri: str, app_code: str):
        self.broker_url = celery_broker_url
        self.backend_uri = celery_result_backend
        self.monitor_redis_uri = monitor_redis_uri
        self.app_code = app_code
        self.default_expire_seconds = 12 * 3600
        self.celery_client = Celery(
            'zcbot-predict',
            broker=self.broker_url,
            backend=self.backend_uri,
            task_acks_late=True
        )
        self.rds_client = Redis.from_url(url=monitor_redis_uri, decode_responses=True)
        self.task_map = dict()

    def apply_group(self, task_name: str, task_params_list: List[Dict] = None, options: Dict = None, callback: Callback = None, queue_name: str = None, timeout: float = None, **kwargs):
        """
        服务组调用
        :param task_name: 任务名称
        :param task_params_list: 任务参数清单
        :param timeout: 【可选参数】超时时间
        :param queue_name: 【可选参数】任务队列名称，默认`task.{task_name}`
        :param options: 【可选参数】配置项
        :param callback: 【可选参数】回调函数
        :param kwargs:
        :return:
        """
        try:
            # 同步/异步
            _headers = {'app_code': self.app_code}
            if callback and callback.app_code:
                _headers['app_code'] = callback.app_code or self.app_code

            # 调用
            task_list = []
            for task_params in task_params_list:
                task_list.append(self.get_task_by_name(task_name).signature(kwargs=task_params, options=options))
            task_group = group(task_list)
            _queue_name = queue_name or f'task.{task_name}'
            async_result = task_group.apply_async(queue=_queue_name, headers=_headers)

            # 结果
            if callback:
                # 【异步】绑定回调处理函数
                LOGGER.info(f'[服务组]异步调用 task={task_name}')
                self._bind_callback(task_name, async_result, callback)
                return async_result
            else:
                # 【同步】等待结果
                LOGGER.info(f'[服务组]同步调用 task={task_name}')
                _timeout = timeout or 60
                if not timeout and kwargs and kwargs.get('timeout', None):
                    _timeout = float(kwargs.get('timeout'))
                async_result.successful()
                rs = async_result.get(timeout=_timeout)
                async_result.forget()
                return rs
        except Exception as e:
            LOGGER.error(f'处理异常: task_name={task_name}, kwargs={len(task_params_list)}, e={e}')
            raise e

    def apply(self, task_name: str, task_params: Dict = None, callback: Callback = None, queue_name: str = None, timeout: float = None, **kwargs):
        """
        单任务请求调用
        :param task_name: 任务名称
        :param task_params: 任务参数字典
        :param callback:【可选参数】回调函数
        :param queue_name:【可选参数】任务队列名称，默认`task.{task_name}`
        :param timeout:【可选参数】超时时间
        :param kwargs:
        :return:
        """
        try:
            # 同步/异步
            _headers = {'app_code': self.app_code}
            if callback and callback.app_code:
                _headers['app_code'] = callback.app_code or self.app_code
            # 调用
            _queue_name = queue_name or f'task.{task_name}'
            async_result = self.get_task_by_name(task_name).apply_async(kwargs=task_params, queue=_queue_name, headers=_headers)
            # 结果
            if callback:
                # 【异步】绑定回调处理函数
                LOGGER.info(f'[服务]异步调用 task={task_name}')
                self._bind_callback(task_name, async_result, callback)
                return async_result
            else:
                # 【同步】等待结果
                LOGGER.info(f'[服务]同步调用 task={task_name}')
                _timeout = timeout or 60
                if not timeout and kwargs and kwargs.get('timeout', None):
                    _timeout = float(kwargs.get('timeout'))
                rs = async_result.get(timeout=_timeout)
                async_result.forget()
                return rs
        except Exception as e:
            LOGGER.error(f'处理异常: task_name={task_name}, kwargs={task_params}, e={e}')
            raise e

    # 缓存Celery任务对象
    def get_task_by_name(self, task_name: str):
        task = self.task_map.get(task_name)
        if not task:
            task = Task()
            task.bind(self.celery_client)
            task.name = task_name
            self.task_map[task_name] = task

        return task

    # 异步结果处理函数绑定
    def _bind_callback(self, task_name: str, async_result: AsyncResult, callback: Callback):
        rs_key = get_result_key(app_code=self.app_code, task_name=task_name, task_id=async_result.id)
        self.rds_client.set(rs_key, callback.json(), ex=self.default_expire_seconds)

    # 构建回调对象
    def build_callback(self, callback_func: Union[str, Callable] = None, callback_data: Union[str, Dict, List] = None, app_code: str = None, tenant_code: str = None):
        callback = Callback()
        callback.app_code = app_code or self.app_code
        callback.tenant_code = tenant_code or None
        callback.callback_data = callback_data or None
        if isinstance(callback_func, str):
            callback.callback_func = callback_func
        else:
            callback.callback_func = obj_to_ref(callback_func)

        return callback


class PredictClientHolder(object):
    __default_instance = None

    @staticmethod
    def init_default_instance(celery_broker_url: str, celery_result_backend: str, monitor_redis_uri: str, app_code: str):
        if not PredictClientHolder.__default_instance:
            PredictClientHolder.__default_instance = PredictClient(celery_broker_url, celery_result_backend, monitor_redis_uri, app_code)

    @staticmethod
    def get_default_instance():
        if not PredictClientHolder.__default_instance:
            raise BizException(f'默认实例尚未初始化，请先初始化实例！')
        return PredictClientHolder.__default_instance
