import time

from atlas_engine_client.core.api import ManualTaskQuery

from robot.api import logger

from ._retry_helper import retry_on_exception
class ManualTaskKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

        self._max_retries = kwargs.get('max_retries', 5)
        self._backoff_factor = kwargs.get('backoff_factor', 2)
        self._delay = kwargs.get('delay', 0.1)

    @retry_on_exception
    def get_manual_task_by(self, **kwargs):

        logger.debug(kwargs)

        query = ManualTaskQuery(**kwargs)

        logger.info(query)

        current_retry = 0
        current_delay = float(kwargs.get('delay', self._delay))
        backoff_factor = float(kwargs.get('backoff_factor', self._backoff_factor))
        max_retries = int(kwargs.get('max_retries', self._max_retries))

        while True:
            manual_tasks = self._client.manual_task_get(query)

            logger.info(manual_tasks)

            if len(manual_tasks) >= 1:
                manual_task = manual_tasks[0]
            else:
                manual_task = {}

            if manual_task:
                break
            else:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * backoff_factor
                if current_retry > max_retries:
                    break
                logger.info(f" Retry count: {current_retry} of {max_retries}; delay: {current_delay} and backoff_factor: {backoff_factor}")

        return manual_task

    @retry_on_exception
    def finish_manual_task(self, manual_task_instance_id: str, **kwargs):
        self._client.manual_task_finish(manual_task_instance_id)
