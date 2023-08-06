from ..client import PredictClient, PredictClientHolder


class BaseService(object):
    """
    基础服务
    """

    def __init__(self, celery_client: PredictClient = None):
        self.celery_client = celery_client

    def get_client(self):
        return self.celery_client or PredictClientHolder.get_default_instance()
