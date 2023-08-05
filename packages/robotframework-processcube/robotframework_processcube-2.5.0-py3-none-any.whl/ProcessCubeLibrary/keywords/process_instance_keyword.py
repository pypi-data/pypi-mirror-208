import json
import time
from typing import Dict, Any
from dataclasses import fields

from atlas_engine_client.core.api import FlowNodeInstancesQuery
from atlas_engine_client.core.api import FlowNodeInstanceResponse

from robot.api import logger

from ._fields_helper import filter_kwargs_for_dataclass
from ._retry_helper import retry_on_exception


class ProcessInstanceKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

        self._max_retries = kwargs.get('max_retries', 5)
        self._backoff_factor = kwargs.get('backoff_factor', 2)
        self._delay = kwargs.get('delay', 0.1)

    def get_active_processinstances_by_correlation(self, correlation) -> FlowNodeInstanceResponse:
        query_dict = {
            'state': 'running',
            'correlation_id': correlation
        }

        logger.info(f"query_dict: {query_dict}")

        result = self.get_processinstances_by_query(**query_dict)

        return result

    def get_processinstances_by_correlation(self, correlation) -> FlowNodeInstanceResponse:
        query_dict = {
            'correlation_id': correlation
        }

        logger.info(f"query_dict: {query_dict}")

        result = self.get_processinstances_by_query(**query_dict)

        return result

    def get_active_processinstances_by_processmodel(self, process_model) -> FlowNodeInstanceResponse:
        query_dict = {
            'state': 'running',
            'process_model_id': process_model
        }

        result = self.get_processinstances_by_query(**query_dict)

        return result

    def get_processinstances_by_processmodel(self, process_model) -> FlowNodeInstanceResponse:
        query_dict = {
            'process_model_id': process_model
        }

        result = self.get_processinstances_by_query(**query_dict)

        return result

    @retry_on_exception
    def get_processinstances_by_query(self, **query_dict) -> FlowNodeInstanceResponse:
        result = self._client.process_instanceq_query(FlowNodeInstancesQuery(**query_dict))

        return result

    @retry_on_exception
    def get_processinstance(self, **kwargs) -> FlowNodeInstanceResponse:
        return self._get_processinstance(**kwargs)

    @retry_on_exception
    def get_processinstance_result(self, **kwargs) -> Dict[str, Any]:
        result = self._get_processinstance(**kwargs)

        if result and len(result.tokens) > 0:
            payload = result.tokens[0]['payload']
            if payload is not None:
                try:
                    logger.info(f"type(payload) {type(payload)}")
                    if type(payload) in [str, bytes]:
                        payload = json.loads(payload)
                    else:
                        pass
                except json.decoder.JSONDecodeError:
                    payload = {}
        else:
            payload = {}


        return payload

    def _get_processinstance(self, **kwargs) -> FlowNodeInstanceResponse:

        query_dict = {
            'state': 'finished',
            'limit': 1,
            'flow_node_type': 'bpmn:EndEvent',
        }

        current_retry = 0
        current_delay = float(kwargs.get('delay', self._delay))
        backoff_factor = float(kwargs.get('backoff_factor', self._backoff_factor))
        max_retries = int(kwargs.get('max_retries', self._max_retries))

        local_kwargs = filter_kwargs_for_dataclass(FlowNodeInstancesQuery, kwargs)

        query_dict.update(**local_kwargs)

        while True:

            query = FlowNodeInstancesQuery(**query_dict)

            flow_node_instances = self._client.flow_node_instance_get(query)

            if len(flow_node_instances) == 1:
                flow_node_instance = flow_node_instances[0]
            else:
                flow_node_instance = None

            if flow_node_instance:
                break
            else:
                time.sleep(current_delay)
                current_retry = current_retry + 1
                current_delay = current_delay * backoff_factor
                if current_retry > max_retries:
                    break
                logger.info(f" Retry count: {current_retry} of {max_retries}; delay: {current_delay} and backoff_factor: {backoff_factor}")

        return flow_node_instance
