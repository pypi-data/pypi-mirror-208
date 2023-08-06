# -*- coding: utf-8 -*-
import json
import traceback
from threading import Thread
from celery import Celery, exceptions
from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from redis import Redis
from .common import thread_pool
from .common.keys import get_result_key_filter, get_task_id_from_key
from .common.utils import ref_to_obj, singleton

LOGGER = get_task_logger(__name__)


@singleton
class PredictRedisResultMonitor(object):
    """
    每个应用中仅可启动一个实例
    """

    def __init__(self, celery_broker_url: str, celery_result_backend: str, monitor_redis_uri: str, app_code: str):
        self.broker_url = celery_broker_url
        self.backend_uri = celery_result_backend
        self.monitor_redis_uri = monitor_redis_uri
        self.app_code = app_code

        self.celery_client = Celery(
            'zcbot-predict',
            broker=self.broker_url,
            backend=self.backend_uri,
            task_acks_late=True
        )
        self.rds_client = Redis.from_url(url=monitor_redis_uri, decode_responses=True)

    def start(self):
        Thread(target=self._watch, name='predict-monitor').start()
        LOGGER.info(f'启动Predict结果监听服务...')

    def _watch(self):
        # 当前：每个app一个结果监视器
        while True:
            filter_key = get_result_key_filter(app_code=self.app_code)
            keys = self.rds_client.keys(filter_key)
            # LOGGER.debug(f'扫描[{threading.currentThread()}]: keys={len(keys)}')
            if keys:
                for key in keys:
                    task_id = get_task_id_from_key(key)
                    if task_id:
                        async_result = AsyncResult(id=task_id, app=self.celery_client)
                        if async_result.successful():
                            # 完成
                            try:
                                result = async_result.get()
                                callback = json.loads(self.rds_client.get(key))
                                callback_func = callback.get('callback_func', None)
                                callback_data = callback.get('callback_data', None)
                                if callback_func:
                                    # TODO 兼容线程与协程
                                    func = ref_to_obj(callback_func)
                                    thread_pool.submit(func, result, callback_data)
                                else:
                                    LOGGER.warning(f'无回调: task={task_id}')
                                # 清理
                                self._remove_task(key, async_result)
                            except exceptions.TimeoutError as te:
                                LOGGER.error(f'异常: 结果获取超时 task={task_id}, e={traceback.format_exc()}')
                            except LookupError as le:
                                LOGGER.error(f'异常: 回调函数反序列化异常 task={task_id}, e={traceback.format_exc()}')
                            except Exception as e:
                                LOGGER.error(f'异常: 结果处理异常 task={task_id}, e={traceback.format_exc()}')
                        elif async_result.failed():
                            # 失败
                            self._remove_task(key, async_result)
                            LOGGER.error(f'失败: task={task_id}')

    def _remove_task(self, key, async_result):
        # 清理任务
        async_result.forget()
        self.rds_client.delete(key)
