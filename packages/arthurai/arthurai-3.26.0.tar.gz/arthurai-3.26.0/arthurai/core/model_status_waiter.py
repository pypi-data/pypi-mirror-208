import logging
import threading
import time
from http import HTTPStatus
from typing import List

from yaspin import yaspin

from arthurai.client.http.requests import HTTPClient
from arthurai.common.constants import ModelStatus
from arthurai.common.exceptions import ExpectedParameterNotFoundError, ArthurInternalError

logger = logging.getLogger(__name__)


class ModelStatusWaiter:
    def __init__(self, model_id: str, client: HTTPClient):
        self.model_id = model_id
        self._client = client
        self._status = None
        self._model_status_exception: bool = False
        self._model_status_available = threading.Event()

    def wait_for_valid_model_status(self, status_list: List, spinner_message: str,
                                    update_message: str, update_interval_seconds=60) -> ModelStatus:
        """ Wait for the model to reach a status on the status_list

        Starts the thread that is responsible for checking the status of the model until it reaches a status
        passed in the list as argument or an exception occurs, and runs a spinner providing updates while waiting for it.

        :param status_list: List of :class:`arthurai.common.constants.ModelStatus` list of valid model status
        :param spinner_message: The message you want to display when spinner is running and waiting for results
        :param update_message: The message you want to display when update_interval_seconds time is exceeded
        :param update_interval_seconds: Frequency at which tan update is provided on the console
        """

        self._model_status_available.clear()
        self._model_status_exception = False
        thread = threading.Thread(target=self._await_model_final_status_thread, args=[status_list])
        thread.start()

        with yaspin(text=spinner_message) as sp:
            while not self._model_status_available.wait(timeout=update_interval_seconds):
                sp.write(update_message)
            sp.stop()

        if self._model_status_exception is True:
            raise ArthurInternalError(
                "Failed when trying to fetch the status of the model. Please retry to wait for the status of the model.")

        return self._status


    def _await_model_final_status_thread(self, status_list: List, poll_interval_seconds=5):
        """ Thread that polls the model status

        Polls the model status until it reaches a status in the status_list or an exception occurs.
        This method is used as a thread and sets the flag model_status_available at the end of execution.
        Do not use as a regular function.
        :param status_list: List of :class:`arthurai.common.constants.ModelStatus` list of valid model status
        :param poll_interval_seconds: polling interval to check status on the model
        """
        while True:
            try:
                self._update_model_status()
            except BaseException as ex:
                logger.exception(ex)
                self._model_status_exception = True
                self._model_status_available.set()  # setting the flag on the threading event when result is available
                break
            if self._status in status_list:  # if the status is in status_list, set the flag and break
                self._model_status_available.set()  # setting the flag on the threading event when result is available
                break
            time.sleep(poll_interval_seconds)

    def _update_model_status(self):
        """Updates the latest `status` field of the current model"""
        model_resp = self._client.get(f'/models/{self.model_id}', return_raw_response=True,
                                      validation_response_code=HTTPStatus.OK)
        model_resp_json = model_resp.json()
        if 'id' not in model_resp_json:
            raise ExpectedParameterNotFoundError(
                f"An error occurred: {model_resp}, {model_resp.status_code}, {model_resp.content}")
        self._status = model_resp_json['status']