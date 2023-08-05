
from atlas_engine_client.core.api import ProcessStartRequest
from atlas_engine_client.core.api import StartCallbackType

from ._retry_helper import retry_on_exception


class StartKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

    @retry_on_exception
    def start_processmodel_and_wait(self, process_model, payload={}, **kwargs):
        start_properties = {
            'process_model_id': process_model,
            'initial_token': payload,
            'return_on': StartCallbackType.CallbackOnProcessInstanceFinished
        }

        start_properties.update(kwargs)

        request = ProcessStartRequest(**start_properties)

        result = self._client.process_model_start(process_model, request)

        return result

    @retry_on_exception
    def start_processmodel(self, process_model, payload={}, **kwargs):
        start_properties = {
            'process_model_id': process_model,
            'initial_token': payload,
            'return_on': StartCallbackType.CallbackOnProcessInstanceCreated
        }

        start_properties.update(kwargs)

        request = ProcessStartRequest(**start_properties)

        result = self._client.process_model_start(process_model, request)

        return result
